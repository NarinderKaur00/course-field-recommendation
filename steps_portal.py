"""
steps_portal.py
---------------
ZenML steps that build the PORTAL's model bundle. They reuse the portal's own
training code (portal/ml_core.py), so the model ZenML produces is exactly the
one the website serves — one clean MLOps-to-product story.
"""
import os
import sys
import logging

import pandas as pd
from zenml import step

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "portal"))
from ml_core import train_bundle_from_dataframe  # noqa: E402

MODELS_DIR = os.path.join(HERE, "portal", "models")


@step(enable_cache=False)
def load_portal_data(data_path: str) -> pd.DataFrame:
    """Load the (relabeled Thapar) student-grades dataset."""
    logging.info("Loading portal dataset: %s", data_path)
    return pd.read_csv(data_path, na_values=["NA"])


@step
def train_portal_models(df: pd.DataFrame) -> dict:
    """Train all 14 elective models and save portal/models/bundle.joblib."""
    accuracies = train_bundle_from_dataframe(df, MODELS_DIR)
    logging.info("Saved portal bundle to %s", MODELS_DIR)
    return accuracies


@step
def report_portal_models(accuracies: dict) -> dict:
    """Print a held-out accuracy summary for the ZenML dashboard/logs."""
    print("\nPortal model — held-out accuracy per elective:")
    for subject, acc in accuracies.items():
        bar = "#" * int(acc * 20)
        print(f"  {subject:<8} {acc*100:5.1f}%  {bar}")
    avg = sum(accuracies.values()) / len(accuracies)
    print(f"  Average: {avg*100:.1f}%")
    return accuracies
