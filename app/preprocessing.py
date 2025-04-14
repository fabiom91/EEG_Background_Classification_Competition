import os
import mne
import pandas as pd
from tqdm.auto import tqdm

def preprocess_data(data_path):
    mne.set_log_level('ERROR')
    labels = pd.read_csv(os.path.join(data_path, 'eeg_grades.csv'))
    labels = labels[['file_ID', 'grade']]
    
    edf_files = []
    for root, _, files in os.walk(data_path):
        for file in files:
            if file.endswith('.edf'):
                edf_files.append(os.path.join(root, file))

    raw_eeg_data = {}
    i = 0
    for edf_file in (pbar := tqdm(sorted(edf_files), total = len(edf_files))):
        i += 1
        pbar.set_description(f"Processing {edf_file} - file {i}/{len(edf_files)}")
        file_id = edf_file.split('/')[-1].replace('.edf', '')
        raw = mne.io.read_raw_edf(edf_file, preload=True)
        # Preprocessing steps
        raw.resample(64) # downsample to 64Hz
        raw.filter(0.5, 30)  # band-pass filter as an example
        raw_eeg_data[file_id] = raw.get_data()

    return raw_eeg_data, labels