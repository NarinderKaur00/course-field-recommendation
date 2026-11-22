"""Benchmark every classical ML model, then print the full report.

Usage:
    python run_benchmark_pipeline.py                       # real data (335 students)
    python run_benchmark_pipeline.py --augmented           # + 200 synthetic (535)
    python run_benchmark_pipeline.py ./data/Other.csv
"""
import logging
import subprocess
import sys

from pipelines.benchmark_pipeline import benchmark_pipeline

REAL = "./data/Grade_CS_Students.csv"
AUGMENTED = "./data/Grade_CS_Students_augmented.csv"

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--augmented":
        data_path = AUGMENTED
    elif args:
        data_path = args[0]
    else:
        data_path = REAL

    logging.info("Starting benchmark pipeline")
    print(f"\nDataset: {data_path}\n")
    benchmark_pipeline(data_path)

    # Fresh process: the client in this one holds a stale view of the new run.
    subprocess.run([sys.executable, "benchmark_report.py"], check=True)
