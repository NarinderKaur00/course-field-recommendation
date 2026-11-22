"""
portal_pipeline.py
------------------
ZenML pipeline that produces the model the student portal serves.

    load_portal_data -> train_portal_models -> report_portal_models

Running it writes portal/models/bundle.joblib (tracked by ZenML) which the
Flask portal then loads. This is the bridge that makes the ZenML/MLOps half
power the actual product.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from steps_portal import (  # noqa: E402
    load_portal_data, train_portal_models, report_portal_models,
)
from zenml import pipeline  # noqa: E402


@pipeline
def portal_pipeline(data_path: str):
    df = load_portal_data(data_path)
    accuracies = train_portal_models(df)
    report_portal_models(accuracies)
