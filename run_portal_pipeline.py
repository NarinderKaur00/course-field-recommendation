"""Run the ZenML pipeline that trains the PORTAL's model.

This produces portal/models/bundle.joblib — the exact model the website serves —
but does it as a tracked, reproducible ZenML pipeline (visible in the dashboard).

Usage:
    set PYTHONIOENCODING=utf-8
    python run_portal_pipeline.py
    # then view it:  zenml login --local --blocking   ->  http://127.0.0.1:8237
"""
import logging
import os

from pipelines.portal_pipeline import portal_pipeline

logging.basicConfig(level=logging.INFO, format="%(message)s")

DATA_PATH = os.path.join(".", "data", "Grade_Thapar_Students.csv")

if __name__ == "__main__":
    if not os.path.exists(DATA_PATH):
        print("Dataset missing — run:  python portal/build_thapar_dataset.py")
        raise SystemExit(1)
    print(f"\nTraining the portal model via ZenML pipeline on: {DATA_PATH}\n")
    portal_pipeline(DATA_PATH)
    print("\nDone. portal/models/bundle.joblib is updated — the portal will serve it.")
