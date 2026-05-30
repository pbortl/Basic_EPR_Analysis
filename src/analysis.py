import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter, find_peaks

# === STAŁE FIZYCZNE ===
PLANCK_H = 6.62607015e-34  # [J*s]
MU_BOHR = 9.274009994e-24  # [J/T]


def calculate_g_factor(b_resonance_mt, frequency_ghz):
    nu_hz = frequency_ghz * 1e9
    return (PLANCK_H * nu_hz) / (MU_BOHR * b_resonance_mt * 1e-3)


def analyze_spectrum(b_field, y_values, accumulation_count, expected_lines, smoothing_points, frequency_ghz, u_frequency_ghz):
    # Sprawdzenie, czy dane są wystarczające do analizy
    if len(b_field) < 5 or len(y_values) < 5: # Minimalna liczba punktów dla sensownej analizy
        print("[OSTRZEŻENIE] Zbyt mało punktów danych do przeprowadzenia pełnej analizy. Zwracam domyślne wartości.")
        return {
            "b_resonance": np.nan, "line_count": 0, "coupling_a": np.nan,
            "delta_b_pp": np.nan, "amplitude_pp": np.nan, "global_delta_b_pp": np.nan,
            "global_amplitude_pp": np.nan, "integral_intensity": np.nan,
            "peaks_b": [], "peaks_y": [], "y_analyzed": y_values,
            "idx_max": np.nan, "idx_min": np.nan, "g_factor": np.nan,
            "u_g_factor": np.nan, "u_delta_b_pp": np.nan, "u_amplitude_pp": np.nan
        }

    y_norm = y_values / accumulation_count

    # 1. Korekcja linii bazowej (Baseline Correction)
    baseline_points_fraction = 0.05 # 5% punktów z każdego końca
    num_points_for_baseline = int(len(y_norm) * baseline_points_fraction)
    
    if num_points_for_baseline > 0 and len(y_norm) > 2 * num_points_for_baseline:
        baseline_region = np.concatenate((y_norm[:num_points_for_baseline], y_norm[-num_points_for_baseline:]))
        baseline_offset = np.mean(baseline_region)
        y_norm_corrected = y_norm - baseline_offset
    else:
        y_norm_corrected = y_norm
    
    y_analyzed = savgol_filter(y_norm_corrected, window_length=smoothing_points, polyorder=3) if smoothing_points > 3 else y_norm_corrected

    idx_max, idx_min = np.argmax(y_analyzed), np.argmin(y_analyzed)
    
    # Obliczenia podstawowych parametrów
    global_delta_b_pp = abs(b_field[idx_min] - b_field[idx_max])
    global_amplitude_pp = abs(y_analyzed[idx_max] - y_analyzed[idx_min])

    line_count, coupling_a, peaks_b, peaks_y = 1, 0.0, [], []
    single_line_delta_b_pp = global_delta_b_pp # Domyślnie, dla singletu to samo co globalne
    single_line_amplitude_pp = global_amplitude_pp # Domyślnie, dla singletu to samo co globalne

    if expected_lines != 1: # Jeśli spodziewamy się multipletu lub auto-detekcji
        topo_window = min(51, len(y_norm_corrected) - (1 if len(y_norm_corrected) % 2 == 0 else 0))
        if topo_window < 3: # Zapewnienie minimalnej długości okna dla savgol_filter
            topo_window = 3
        y_topo = savgol_filter(y_norm_corrected, window_length=topo_window, polyorder=3) if topo_window > 3 else y_norm_corrected
        
        # Użyj prominence do lepszej detekcji pików
        prominence_threshold = abs(np.max(y_topo) - np.min(y_topo)) * 0.1
        distance_threshold = max(1, len(y_norm_corrected) // 20) # Minimalna odległość między pikami

        peak_indices, props = find_peaks(y_topo, prominence=prominence_threshold, distance=distance_threshold)

        if expected_lines and len(peak_indices) != expected_lines:
            if len(peak_indices) > expected_lines:
                # Wybierz najbardziej prominentne piki
                peak_indices = np.sort(peak_indices[np.argsort(props['prominences'])[-expected_lines:]])
            elif len(peak_indices) < expected_lines:
                # Jeśli wykryto mniej niż oczekiwano, użyj tego co jest
                pass

        line_count = max(1, len(peak_indices))
        if line_count > 1:
            peaks_b = b_field[peak_indices]
            peaks_y = y_analyzed[peak_indices]
            
            # 2. Wyznaczanie szerokości linii dla multipletów (pojedynczej linii)
            if len(peak_indices) > 0:
                chosen_peak_idx_in_y_analyzed = peak_indices[0] # Indeks pierwszego piku w y_analyzed
                
                # Określ okno wyszukiwania wokół piku
                # Użyj np. 1/3 odległości między pikami jako przybliżonej szerokości połówkowej
                # lub stałej wartości, jeśli coupling_a jest małe
                if len(peaks_b) > 1:
                    avg_peak_distance = np.mean(np.diff(peaks_b))
                    window_half_mT = avg_peak_distance / 2.0 # Połowa odległości między pikami
                else:
                    window_half_mT = global_delta_b_pp / 4.0 if global_delta_b_pp > 0 else (b_field[-1] - b_field[0]) / 10.0 # Domyślna wartość

                # Przelicz window_half_mT na liczbę punktów
                points_per_mT = len(b_field) / (b_field[-1] - b_field[0]) if (b_field[-1] - b_field[0]) != 0 else 1
                window_half_points = int(window_half_mT * points_per_mT)
                
                search_start_idx = max(0, chosen_peak_idx_in_y_analyzed - window_half_points)
                search_end_idx = min(len(y_analyzed), chosen_peak_idx_in_y_analyzed + window_half_points)
                
                if search_end_idx > search_start_idx:
                    local_segment_y = y_analyzed[search_start_idx:search_end_idx]
                    local_segment_b = b_field[search_start_idx:search_end_idx]

                    if len(local_segment_y) > 0:
                        local_min_idx_rel = np.argmin(local_segment_y)
                        local_max_idx_rel = np.argmax(local_segment_y)
                        
                        single_line_delta_b_pp = abs(local_segment_b[local_min_idx_rel] - local_segment_b[local_max_idx_rel])
                        single_line_amplitude_pp = abs(local_segment_y[local_max_idx_rel] - local_segment_y[local_min_idx_rel])
                    else:
                        single_line_delta_b_pp = 0.0
                        single_line_amplitude_pp = 0.0
                else:
                    single_line_delta_b_pp = 0.0
                    single_line_amplitude_pp = 0.0
            else:
                single_line_delta_b_pp = 0.0
                single_line_amplitude_pp = 0.0


    if line_count > 1:
        coupling_a = (peaks_b[-1] - peaks_b[0]) / (line_count - 1) if line_count > 1 else 0.0
        b_resonance = (peaks_b[0] + peaks_b[-1]) / 2.0
    else:
        # Singlet analysis
        # Upewnij się, że idx_max i idx_min są poprawne i nie są takie same
        if idx_max == idx_min: # Jeśli sygnał jest płaski lub ma tylko jeden punkt
            b_resonance = b_field[idx_max] if len(b_field) > idx_max else np.nan
        else:
            # Upewnij się, że zakres jest prawidłowy
            start_idx = min(idx_max, idx_min)
            end_idx = max(idx_max, idx_min) + 1
            
            if end_idx > start_idx and end_idx <= len(b_field):
                range_b = b_field[start_idx:end_idx]
                range_y = y_analyzed[start_idx:end_idx]
                
                if len(range_b) > 1 and len(range_y) > 1:
                    try:
                        b_resonance = float(interp1d(range_y, range_b, kind='linear', fill_value="extrapolate")(0.0))
                    except ValueError: # Może się zdarzyć, jeśli 0.0 jest poza zakresem range_y
                        b_resonance = np.mean([b_field[idx_max], b_field[idx_min]])
                else:
                    b_resonance = np.mean([b_field[idx_max], b_field[idx_min]])
            else:
                b_resonance = np.mean([b_field[idx_max], b_field[idx_min]])


    abs_curve = cumulative_trapezoid(y_norm_corrected, b_field, initial=0)
    integral_intensity = abs(cumulative_trapezoid(abs_curve, b_field, initial=0)[-1])

    # === Obliczanie niepewności ===
    u_b_pos = (b_field[1] - b_field[0]) / 2.0 if len(b_field) > 1 else 0.0 # Niepewność pozycji pola (połowa kroku)
    u_y = np.std(y_analyzed) if len(y_analyzed) > 1 else 0.0 # Niepewność intensywności (std dev sygnału)

    # Niepewność g-faktora
    g_factor = calculate_g_factor(b_resonance, frequency_ghz)
    
    u_nu_rel_sq = (u_frequency_ghz / frequency_ghz)**2 if frequency_ghz != 0 else 0
    u_b_res_rel_sq = (u_b_pos / b_resonance)**2 if b_resonance != 0 else 0
    u_g_factor = g_factor * np.sqrt(u_nu_rel_sq + u_b_res_rel_sq) if g_factor != 0 else np.nan

    # Niepewność szerokości linii delta_b_pp
    u_delta_b_pp = u_b_pos * np.sqrt(2)

    # Niepewność amplitudy amplitude_pp
    u_amplitude_pp = u_y * np.sqrt(2)


    return {
        "b_resonance": b_resonance,
        "line_count": line_count,
        "coupling_a": coupling_a,
        "delta_b_pp": single_line_delta_b_pp if line_count > 1 else global_delta_b_pp, # Zwracaj szerokość pojedynczej linii dla multipletów
        "amplitude_pp": single_line_amplitude_pp if line_count > 1 else global_amplitude_pp, # Zwracaj amplitudę pojedynczej linii dla multipletów
        "global_delta_b_pp": global_delta_b_pp, # Dodaj globalną szerokość dla informacji
        "global_amplitude_pp": global_amplitude_pp, # Dodaj globalną amplitudę dla informacji
        "integral_intensity": integral_intensity,
        "peaks_b": peaks_b,
        "peaks_y": peaks_y,
        "y_analyzed": y_analyzed,
        "idx_max": idx_max,
        "idx_min": idx_min,
        "g_factor": g_factor,
        "u_g_factor": u_g_factor,
        "u_delta_b_pp": u_delta_b_pp,
        "u_amplitude_pp": u_amplitude_pp
    }
