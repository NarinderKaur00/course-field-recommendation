"""Score every model on every target with a full set of classification metrics."""
import logging

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    cohen_kappa_score,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
)
from zenml import step

# Displayed left to right in the report.
METRICS = ["accuracy", "balanced_acc", "precision", "recall", "f1_weighted",
           "f1_macro", "cohen_kappa", "mcc"]


def score(y_test, y_pred) -> dict:
    """All metrics for one (model, target) pair."""
    kw = {"average": "weighted", "zero_division": 0}
    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "balanced_acc": balanced_accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, **kw),
        "recall": recall_score(y_test, y_pred, **kw),
        "f1_weighted": f1_score(y_test, y_pred, **kw),
        "f1_macro": f1_score(y_test, y_pred, average="macro", zero_division=0),
        "cohen_kappa": cohen_kappa_score(y_test, y_pred),
        "mcc": matthews_corrcoef(y_test, y_pred),
    }


@step
def evaluate_models(train_results: dict) -> dict:
    """
    Args:
        train_results: {target: {model: {y_test, y_pred}}}
    Returns:
        results: {target: {model: {metric: value}}}
    """
    results = {}

    for target, per_model in train_results.items():
        logging.info(f"Evaluating all models for: {target}")
        results[target] = {
            name: score(r["y_test"], r["y_pred"]) for name, r in per_model.items()
        }

    return results
