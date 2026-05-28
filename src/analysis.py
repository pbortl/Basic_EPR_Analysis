import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter, find_peaks


def calculate_g_factor(b_resonance_mt, frequency_ghz):
    h_planck = 6.62607015e-34
    mu_bohr = 9.274009994e-24
    nu_hz = frequency_ghz * 1e9
    return (h_planck * nu_hz) / (mu_bohr * b_resonance_mt * 1e-3)


def analyze_spectrum(b_field, y_values, accumulation_count, expected_lines, smoothing_points):
    y_norm = y_values / accumulation_count
    y_analyzed = savgol_filter(y_norm, window_length=smoothing_points, polyorder=3) if smoothing_points > 3 else y_norm

    idx_max, idx_min = np.argmax(y_analyzed), np.argmin(y_analyzed)
    delta_b_pp = abs(b_field[idx_min] - b_field[idx_max])
    amplitude_pp = abs(y_analyzed[idx_max] - y_analyzed[idx_min]) # Dodane wyliczenie amplitudy

    line_count, coupling_a, peaks_b, peaks_y = 1, 0.0, [], []

    if expected_lines != 1:
        topo_window = min(51, len(y_norm) - (1 if len(y_norm) % 2 == 0 else 0))
        y_topo = savgol_filter(y_norm, window_length=topo_window, polyorder=3) if topo_window > 3 else y_norm
        peak_indices, props = find_peaks(y_topo, prominence=abs(np.max(y_topo) - np.min(y_topo)) * 0.1,
                                         distance=max(1, len(y_norm) // 20))

        if expected_lines and len(peak_indices) != expected_lines:
            if len(peak_indices) > expected_lines:
                peak_indices = np.sort(peak_indices[np.argsort(props['prominences'])[-expected_lines:]])

        line_count = max(1, len(peak_indices))
        if line_count > 1:
            peaks_b = b_field[peak_indices]
            peaks_y = y_analyzed[peak_indices]

    if line_count > 1:
        coupling_a = (peaks_b[-1] - peaks_b[0]) / (line_count - 1)
        b_resonance = (peaks_b[0] + peaks_b[-1]) / 2.0
    else:
        # Singlet analysis
        range_b, range_y = (b_field[idx_max:idx_min + 1], y_analyzed[idx_max:idx_min + 1]) if b_field[idx_max] < \
                                                                                              b_field[idx_min] else (
            b_field[idx_min:idx_max + 1], y_analyzed[idx_min:idx_max + 1])
        b_resonance = float(interp1d(range_y, range_b, kind='linear', fill_value="extrapolate")(0.0))

    abs_curve = cumulative_trapezoid(y_norm, b_field, initial=0)
    integral_intensity = abs(cumulative_trapezoid(abs_curve, b_field, initial=0)[-1])

    return {
        "b_resonance": b_resonance,
        "line_count": line_count,
        "coupling_a": coupling_a,
        "delta_b_pp": delta_b_pp,
        "amplitude_pp": amplitude_pp,
        "integral_intensity": integral_intensity,
        "peaks_b": peaks_b,
        "peaks_y": peaks_y,
        "y_analyzed": y_analyzed,
        "idx_max": idx_max,
        "idx_min": idx_min
    }
