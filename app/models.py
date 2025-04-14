import mlflow
import mlflow.sklearn
from tqdm.auto import tqdm
from mlflow.models.signature import infer_signature
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report, make_scorer, matthews_corrcoef
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from skopt import BayesSearchCV
from skopt.space import Real, Integer

def build_pipeline(model_name, use_scaler, use_feature_selection, use_augmentation):
    steps = []

    if use_scaler:
        steps.append(("scaler", RobustScaler()))
    if use_augmentation:
        steps.append(("smote", SMOTE(random_state=42, k_neighbors=1)))
    if use_feature_selection:
        steps.append(("feature_selection", SelectKBest(score_func=f_classif, k=10)))

    steps.append(("classifier", None))  # placeholder, will be set below
    pipeline = Pipeline(steps=steps)

    if model_name == "Logistic Regression":
        model = LogisticRegression(max_iter=1000)
        search_space = {
            "classifier": [model],
            "classifier__C": Real(1e-3, 1e2, prior='log-uniform'),
            "classifier__penalty": ["l2"],
        }
    elif model_name == "Random Forest":
        model = RandomForestClassifier()
        search_space = {
            "classifier": [model],
            "classifier__n_estimators": Integer(50, 200),
            "classifier__max_depth": Integer(2, 20),
        }
    elif model_name == "XGBoost":
        model = XGBClassifier()
        search_space = {
            "classifier": [model],
            "classifier__learning_rate": Real(0.01, 0.3, prior='log-uniform'),
            "classifier__max_depth": Integer(3, 10),
            "classifier__n_estimators": Integer(50, 200),
        }
    else:
        raise ValueError(f"Unsupported model: {model_name}")

    return pipeline, search_space


def evaluate_model_cv(model_name, X, y, num_classes, n_splits=10, use_scaler=False, use_feature_selection=False, use_augmentation=False):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    all_metrics = []

    with mlflow.start_run(run_name=model_name):
        for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            pipeline, search_space = build_pipeline(model_name, use_scaler, use_feature_selection, use_augmentation)
            scorer = make_scorer(matthews_corrcoef, greater_is_better=True)

            search = BayesSearchCV(
                estimator=pipeline,
                search_spaces=search_space,
                n_iter=10,
                cv=3,
                n_jobs=-1,
                scoring=scorer,
                random_state=42,
                verbose=0
            )

            search.fit(X_train, y_train)
            best_model = search.best_estimator_

            # Log the model for this fold as an MLflow artifact.
            # Take a small sample to use as input example
            example_input = X_test.iloc[:5]
            example_output = best_model.predict(example_input)
            signature = infer_signature(example_input, example_output)

            mlflow.sklearn.log_model(
                sk_model=best_model,
                artifact_path=f"model_fold_{fold}",
                signature=signature,
                input_example=example_input
            )

            preds = best_model.predict(X_test)
            report = classification_report(y_test, preds, output_dict=True, zero_division=0)

            metrics = {
                'accuracy': report['accuracy'],
                'precision': report['weighted avg']['precision'],
                'recall': report['weighted avg']['recall'],
                'f1-score': report['weighted avg']['f1-score'],
                'mcc': matthews_corrcoef(y_test, preds),
            }

            for key, value in metrics.items():
                mlflow.log_metric(key, value, step=fold)

            all_metrics.append(metrics)

        # Log average metrics and best hyperparams
        mean_metrics = {
            f"mean_{metric}": np.mean([fold[metric] for fold in all_metrics])
            for metric in all_metrics[0]
        }

        mlflow.log_metrics(mean_metrics)
        mlflow.log_params(search.best_params_)


def run_models(data, use_scaler=False, use_feature_selection=False, use_augmentation=False):
    X = data.drop(columns=['file_id', 'grade'])
    y_raw = data['grade']

    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    num_classes = len(le.classes_)

    model_names = ["Logistic Regression", "Random Forest", "XGBoost"]

    for i, model_name in (pbar := tqdm(enumerate(model_names), total=len(model_names))):
        pbar.set_description(f"Running {model_name} - model {i+1}/{len(model_names)}")
        evaluate_model_cv(
            model_name, X, y, num_classes, n_splits=10,
            use_scaler=use_scaler,
            use_feature_selection=use_feature_selection,
            use_augmentation=use_augmentation
        )
