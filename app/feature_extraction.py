import numpy as np
import pandas as pd
from tqdm.auto import tqdm
import antropy as ant
from scipy.stats import linregress

def extract_features(eeg_data, labels):
    features = pd.DataFrame()
    i = 0
    for file_id, data in (pbar := tqdm(eeg_data.items(), total=len(eeg_data))):
        i += 1
        pbar.set_description(f"Extracting features from {file_id} - file {i}/{len(eeg_data)}")
        data = pd.DataFrame(data).T
        data = data.median(axis=1)
        desc = data.describe().to_dict()
        reg = linregress(data.index, data)
        desc['95%'] = [data.quantile(q=0.95)]
        desc['skew'] = [data.skew()]
        desc['kurtosis'] = [data.kurtosis()]
        desc['linearRegressionSlope'] = [reg.slope]
        desc['linearRegressionIntercept'] = [reg.intercept]
        desc['median'] = [data.median()]
        desc['entropy'] = [ant.perm_entropy(data, normalize=True)]
        desc['hjorth_mob'] = [ant.hjorth_params(data)[0]]
        desc['hjorth_comp'] = [ant.hjorth_params(data)[1]]
        grade = labels.loc[labels['file_ID'] == file_id, 'grade'].values[0]
        desc['file_id'] = [file_id]
        desc['grade'] = [int(grade)]
        feats = pd.DataFrame(desc)
        feats = feats[['std', '25%', '75%', '95%', 'skew', 'kurtosis', 'linearRegressionSlope', 'linearRegressionIntercept', 'median', 'entropy', 'hjorth_mob', 'hjorth_comp', 'file_id', 'grade']]
        features = pd.concat([features, feats], ignore_index=True)

    return features
