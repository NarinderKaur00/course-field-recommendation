"""Run every pipeline in this project back to back, then print a comparison.

Usage:
    python run_all_pipelines.py
    python run_all_pipelines.py ./data/My_Other_Dataset.csv
"""
import logging
import subprocess
import sys
import time

from pipelines.SVM_pipeline import SVM_pipeline
from pipelines.xgb_pipeline import XGB_pipeline
from pipelines.RF_pipeline import RF_pipeline
from pipelines.MLP_pipeline import MLP_pipeline

logging.basicConfig(level=logging.INFO)

PIPELINES = [
    ("SVM (Linear Regression baseline)", SVM_pipeline),
    ("XGBoost", XGB_pipeline),
    ("Random Forest", RF_pipeline),
    ("MLP (Neural Network)", MLP_pipeline),
]


def banner(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n", flush=True)


if __name__ == "__main__":
    data_path = sys.argv[1] if len(sys.argv) > 1 else "./data/Grade_CS_Students.csv"

    banner(f"DATASET: {data_path}")

    timings = []
    for name, pipeline in PIPELINES:
        banner(f"RUNNING: {name}")
        start = time.time()
        pipeline(data_path)
        timings.append((name, time.time() - start))

    banner("PIPELINE RUNTIMES")
    for name, seconds in timings:
        print(f"  {name:<40} {seconds:>6.1f}s")

    banner("MODEL COMPARISON (read back from the ZenML artifact store)")
    # Run in a fresh process: the ZenML client in this process holds a stale
    # view of the runs it just created and reports the wrong run's metrics.
    subprocess.run([sys.executable, "compare_results.py"], check=True)
