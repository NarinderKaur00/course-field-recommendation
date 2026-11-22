import logging
from zenml import step
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
import pandas as pd


@step
def train_RF(
    features_encoded: pd.DataFrame,
    targets_encoded: pd.DataFrame) -> dict:
    """
    Args:
        features_encoded: pd.DataFrame
        targets_encoded: pd.DataFrame
    Returns:
        results: dict
    """
    results = {}

    for column in targets_encoded.columns:

        logging.info(f"Training Random Forest model for target column: {column}")

        smote = SMOTE(k_neighbors=3)
        features_resampled, target_resampled = smote.fit_resample(
            features_encoded, targets_encoded[column])

        X_train, X_test, y_train, y_test = train_test_split(
            features_resampled, target_resampled, test_size=0.2, random_state=42)

        le = LabelEncoder()
        y_train = le.fit_transform(y_train)
        y_test = le.transform(y_test)

        rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)

        # Train the classifier
        rf.fit(X_train, y_train)

        # Predict the target values
        y_pred = rf.predict(X_test)

        results[column] = {
            'y_test': y_test,
            'y_pred': y_pred
        }

    return results
