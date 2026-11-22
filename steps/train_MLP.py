import logging
import os
import warnings

from sklearn.exceptions import ConvergenceWarning
from zenml import step

# The MLP does not always converge within max_iter, which floods the console
# with one ConvergenceWarning per grid-search fit (hundreds of lines).
# GridSearchCV(n_jobs=-1) runs fits in worker processes that do NOT inherit the
# parent's warning filters, so PYTHONWARNINGS is set too -- workers inherit the
# environment. The notebook this step is based on does the same via
# warnings.filterwarnings('ignore').
warnings.filterwarnings("ignore", category=ConvergenceWarning)
os.environ["PYTHONWARNINGS"] = "ignore::sklearn.exceptions.ConvergenceWarning"
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neural_network import MLPClassifier
from imblearn.over_sampling import SMOTE
import pandas as pd

# Reduced version of the grid explored in steps_new/new_MLP_all.ipynb.
# The full grid is ~27k combinations per target, which is not feasible to run
# for all 14 target subjects.
PARAMETERS = {
    "hidden_layer_sizes": [(100,), (50, 25)],
    "activation": ["relu", "tanh"],
    "alpha": [0.0001, 0.01],
}


@step
def train_MLP(
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

        logging.info(f"Training MLP model for target column: {column}")

        smote = SMOTE(k_neighbors=3)
        features_resampled, target_resampled = smote.fit_resample(
            features_encoded, targets_encoded[column])

        X_train, X_test, y_train, y_test = train_test_split(
            features_resampled, target_resampled, test_size=0.2, random_state=42)

        le = LabelEncoder()
        y_train = le.fit_transform(y_train)
        y_test = le.transform(y_test)

        # Standardize the features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Find the best hyperparameters
        clf = MLPClassifier(random_state=42, max_iter=300)
        grid_search = GridSearchCV(clf, PARAMETERS, cv=5, n_jobs=-1)
        grid_search.fit(X_train_scaled, y_train)
        logging.info(f"Best hyperparameters for {column}: {grid_search.best_params_}")

        # Train the classifier with the best hyperparameters
        best_clf = MLPClassifier(random_state=1, max_iter=300, **grid_search.best_params_)
        best_clf.fit(X_train_scaled, y_train)

        # Predict the target values
        y_pred = best_clf.predict(X_test_scaled)

        results[column] = {
            'y_test': y_test,
            'y_pred': y_pred
        }

    return results
