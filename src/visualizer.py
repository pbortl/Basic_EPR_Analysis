import matplotlib
matplotlib.use('Agg')  # Wymusza tryb bez interfejsu graficznego (naprawia błąd init.tcl)
import matplotlib.pyplot as plt
import os


def save_report(filename, results_dict, trans):
    results_dir = os.path.join(os.getcwd(), 'results')
    os.makedirs(results_dir, exist_ok=True)
    base_name = os.path.basename(filename).rsplit('.', 1)[0]
    report_path = os.path.join(results_dir, f"{base_name}_report.txt")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"--- {trans['results_header']} ---\n")
        for key, value in results_dict.items():
            f.write(f"{key}: {value}\n")
    return report_path


def create_plot(b_field, y_analyzed, peaks_b, peaks_y, line_count, idx_max, idx_min, title, save_path, trans,
                smoothing_points):
    plt.figure(figsize=(10, 6))
    label = trans['plot_label_smoothed'].format(n=smoothing_points) if smoothing_points > 3 else trans['plot_label_raw']
    plt.plot(b_field, y_analyzed, label=label, color='blue')

    if line_count > 1:
        plt.scatter(peaks_b, peaks_y, marker='x', color='red', label=trans['plot_peaks'])
    else:
        plt.scatter([b_field[idx_max], b_field[idx_min]], [y_analyzed[idx_max], y_analyzed[idx_min]], color='red', s=30)

    plt.title(title)
    plt.xlabel(trans['axis_x'])
    plt.ylabel(trans['axis_y'])
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
