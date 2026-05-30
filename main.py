import os
import matplotlib
matplotlib.use('Agg')
import sys
from src.config_loader import setup_language
from src.data_loader import resolve_file_path, load_epr_data
from src.analysis import analyze_spectrum # Usunięto calculate_g_factor, bo jest w analyze_spectrum
from src.visualizer import save_report, create_plot


def main():
    trans = setup_language()
    print(f"\n--- {trans['welcome']} ---")

    # 1. File Selection
    user_input_path = input(f"1. {trans['choose_file']}").strip()
    data_file_path = resolve_file_path(user_input_path)
    if not data_file_path:
        print(f"\n[!] {trans['error_not_found']} ({user_input_path})")
        return

    # 2. Parameters
    freq_input = input(f"2. {trans['freq_prompt']}")
    frequency_ghz = float(freq_input.replace(',', '.'))
    
    # Nowe zapytanie o niepewność częstotliwości
    u_freq_input = input(f"2a. Podaj niepewność częstotliwości [GHz] (np. 0.0001, Enter dla 0.0): ")
    u_frequency_ghz = float(u_freq_input.replace(',', '.')) if u_freq_input.strip() else 0.0

    plot_title = input(f"3. {trans['title_prompt']}")
    save_filename = input(f"4. {trans['save_prompt']}")

    # 3. Load Data
    b_field, y_values, accumulation_count, meta = load_epr_data(data_file_path)

    if not data_file_path.endswith('.json'):
        scans_input = input(f"5. {trans['scans_prompt']}")
        accumulation_count = int(scans_input) if scans_input.strip() else 1

    # 4. Analysis
    expected_lines_input = input(f"\n8. {trans['lines_prompt']}")
    expected_lines = int(expected_lines_input.strip()) if expected_lines_input.strip() else None

    # Przekazanie frequency_ghz i u_frequency_ghz do analyze_spectrum
    res = analyze_spectrum(b_field, y_values, accumulation_count, expected_lines, 
                           meta['smoothing_points'], frequency_ghz, u_frequency_ghz)
    
    # g_factor jest teraz zwracany bezpośrednio z analyze_spectrum
    g_factor = res['g_factor']

    # 5. Summary & Export
    summary = {
        trans['accumulations']: accumulation_count,
        trans['g_factor']: f"{g_factor:.6f} +/- {res['u_g_factor']:.6f}", # Zaktualizowane o niepewność
        trans['resonance_field']: f"{res['b_resonance']:.4f} mT",
        trans['integral_intensity']: f"{res['integral_intensity']:.4f}"
    }
    
    if res['line_count'] > 1:
        summary[trans['detected_lines']] = res['line_count']
        summary[trans['coupling_const']] = f"{res['coupling_a']:.4f} mT"
        summary["Szerokość linii (pojedyncza)"] = f"{res['delta_b_pp']:.4f} +/- {res['u_delta_b_pp']:.4f} mT" # Dla multipletów
        summary["Amplituda (pojedyncza)"] = f"{res['amplitude_pp']:.4f} +/- {res['u_amplitude_pp']:.4f}" # Dla multipletów
        summary["Szerokość linii (globalna)"] = f"{res['global_delta_b_pp']:.4f} mT" # Globalna dla informacji
        summary["Amplituda (globalna)"] = f"{res['global_amplitude_pp']:.4f}" # Globalna dla informacji
    else:
        summary[trans['line_width']] = f"{res['delta_b_pp']:.4f} +/- {res['u_delta_b_pp']:.4f} mT" # Dla singletów
        summary["Amplituda"] = f"{res['amplitude_pp']:.4f} +/- {res['u_amplitude_pp']:.4f}" # Dla singletów

    print(f"\n--- {trans['results_header']} ---")
    for key, val in summary.items():
        print(f"{key}: {val}")

    # 6. Saving
    plots_dir = os.path.join(os.getcwd(), 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    full_plot_path = os.path.join(plots_dir, save_filename)

    report_file = save_report(save_filename, summary, trans)
    create_plot(b_field, res['y_analyzed'], res['peaks_b'], res['peaks_y'],
                res['line_count'], res['idx_max'], res['idx_min'],
                plot_title, full_plot_path, trans, meta['smoothing_points'])

    print(f"\n{trans['success_save']} {full_plot_path} & {report_file}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)
