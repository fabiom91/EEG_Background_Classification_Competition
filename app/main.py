import mlflow
from preprocessing import preprocess_data
from feature_extraction import extract_features
from models import run_models
import config
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Run EEG classification pipeline.")
    parser.add_argument("-s", "--scaler", action="store_true", help="Add StandardScaler to the pipeline")
    parser.add_argument("-a", "--augmentation", action="store_true", help="Add SMOTE to the pipeline")
    parser.add_argument("-fs", "--feature_selection", action="store_true", help="Add feature selection to the pipeline")
    return parser.parse_args()

def main():
    args = parse_args()
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(config.EXPERIMENT_NAME)

    raw_data, labels = preprocess_data(config.DATA_PATH)
    data = extract_features(raw_data, labels)

    run_models(data, use_scaler=args.scaler, use_augmentation=args.augmentation, use_feature_selection=args.feature_selection)

if __name__ == "__main__":
    main()
