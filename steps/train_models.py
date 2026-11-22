"""Train a set of classical ML models on every target subject.

Every model sees the SAME SMOTE-resampled train/test split for a given target,
so the comparison between models is fair. All random seeds are fixed, so the
numbers are reproducible from run to run.
"""
import logging

import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
from zenml import step

SEED = 42


def build_models():
    """Classical ML models only -- no deep learning.

    Distance- and gradient-based models (LogReg, KNN, SVM) are wrapped in a
    scaler; the tree ensembles do not need one.
    """
    return {
        "LogReg": make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=1000, random_state=SEED)),
        "NaiveBayes": GaussianNB(),
        "KNN": make_pipeline(
            StandardScaler(), KNeighborsClassifier(n_neighbors=5)),
        "SVM": make_pipeline(
            StandardScaler(), SVC(kernel="rbf", random_state=SEED)),
        "DecisionTree": DecisionTreeClassifier(random_state=SEED),
        "RandomForest": RandomForestClassifier(
            n_estimators=200, random_state=SEED, n_jobs=-1),
        "GradBoost": GradientBoostingClassifier(n_estimators=50, random_state=SEED),
        "XGBoost": XGBClassifier(random_state=SEED, verbosity=0),
    }


@step
def train_models(
    features_encoded: pd.DataFrame,
    targets_encoded: pd.DataFrame) -> dict:
    """
    Args:
        features_encoded: pd.DataFrame
        targets_encoded: pd.DataFrame
    Returns:
        results: dict of {target: {model_name: {y_test, y_pred}}}
    """
    results = {}

    for column in targets_encoded.columns:
        logging.info(f"Training all models for target column: {column}")

        # Resample and split ONCE, so every model is scored on identical data.
        smote = SMOTE(k_neighbors=3, random_state=SEED)
        features_resampled, target_resampled = smote.fit_resample(
            features_encoded, targets_encoded[column])

        X_train, X_test, y_train, y_test = train_test_split(
            features_resampled, target_resampled, test_size=0.2, random_state=SEED)

        le = LabelEncoder()
        y_train = le.fit_transform(y_train)
        y_test = le.transform(y_test)

        per_model = {}
        for name, model in build_models().items():
            logging.info(f"  {column}: fitting {name}")
            model.fit(X_train, y_train)
            per_model[name] = {
                "y_test": y_test,
                "y_pred": model.predict(X_test),
            }

        results[column] = per_model

    return results
