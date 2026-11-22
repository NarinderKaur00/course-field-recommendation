"""
train_models.py
---------------
Run this ONCE to train all 14 elective models and save them to portal/models/.
After this, the web app loads the saved models instantly (no retraining).

Usage:
    python portal/train_models.py
"""

import os
import sys
import logging

# Make sure we can import ml_core whether run from the project root or portal/
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from ml_core import train_and_save  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")

# Dataset lives in ../data relative to this file
PROJECT_ROOT = os.path.dirname(HERE)
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "Grade_Thapar_Students.csv")
MODELS_DIR = os.path.join(HERE, "models")


def main():
    print("=" * 60)
    print(" Training elective-recommendation models")
    print("=" * 60)
    print(f" Dataset : {DATA_PATH}")
    print(f" Output  : {MODELS_DIR}")
    print("-" * 60)

    if not os.path.exists(DATA_PATH):
        print(f"ERROR: dataset not found at {DATA_PATH}")
        sys.exit(1)

    accuracies = train_and_save(DATA_PATH, MODELS_DIR)

    print("\nHeld-out accuracy per elective:")
    for subject, acc in accuracies.items():
        bar = "#" * int(acc * 20)
        print(f"  {subject:<7} {acc*100:5.1f}%  {bar}")

    avg = sum(accuracies.values()) / len(accuracies)
    print("-" * 60)
    print(f" Average accuracy: {avg*100:.1f}%")
    print(" Models saved. You can now run the web app (python portal/app.py)")
    print("=" * 60)


if __name__ == "__main__":
    main()
