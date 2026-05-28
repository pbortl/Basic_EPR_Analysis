import os
import json
import numpy as np


def resolve_file_path(path):
    if os.path.exists(path):
        return path
    data_path = os.path.join(os.getcwd(), 'data', path)
    if os.path.exists(data_path):
        return data_path
    return None


def load_epr_data(file_path):
    b_field_list, intensity_list = [], []
    accumulation_count = 1
    metadata = {"attenuation": "", "modulation": "", "smoothing_points": 0}

    if file_path.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        options = json_data.get('ExperimentOptions', {}).get('CommonOptions', {})
        b_center = options.get('CenterMagneticField', 338.0)
        b_sweep = options.get('SweepWidth', 10.0)
        points_count = options.get('PointsCount', 1000)

        raw_smoothing = options.get('SmoothingPoints', 40)
        metadata['smoothing_points'] = (
            raw_smoothing if raw_smoothing % 2 != 0 else raw_smoothing + 1) if raw_smoothing > 3 else 0

        att_val = options.get('MwParameter', {}).get('AttenuationDb', None)
        metadata['attenuation'] = str(att_val) if att_val is not None else ""

        mod_val = options.get('ModulationAmplitude', None)
        metadata['modulation'] = str(mod_val) if mod_val is not None else ""

        accumulation_count = json_data.get('ExperimentOptions', {}).get('Count2D', 1)

        frames = json_data.get('Values', [])[0].get('Values', [])
        intensity_list = [sum(frame.get('Points', [0])) for frame in frames]
        b_field = b_center - (b_sweep / 2.0) + np.arange(len(intensity_list)) * (b_sweep / (points_count - 1))
    else:
        # Simple TXT/DAT loader
        # This can be expanded later for better TXT parsing
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().replace(',', '.').split()
                if len(parts) >= 2:
                    try:
                        b_field_list.append(float(parts[0]))
                        intensity_list.append(float(parts[1]))
                    except ValueError:
                        continue
        b_field = np.array(b_field_list)
        intensity_list = np.array(intensity_list)

    return b_field, np.array(intensity_list), accumulation_count, metadata
