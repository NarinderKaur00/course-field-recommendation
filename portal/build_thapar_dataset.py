"""
build_thapar_dataset.py
-----------------------
Create data/Grade_Thapar_Students.csv by RELABELING the original
Grade_CS_Students.csv using thapar_map.py.

The grades are the real students' grades; only the column headers change to
Thapar course codes. A disclosure note is written alongside the file.

Usage:  python portal/build_thapar_dataset.py
"""
import os
import sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from thapar_map import FEATURE_MAP, TARGET_MAP  # noqa: E402

PROJECT_ROOT = os.path.dirname(HERE)
SRC = os.path.join(PROJECT_ROOT, "data", "Grade_CS_Students.csv")
OUT = os.path.join(PROJECT_ROOT, "data", "Grade_Thapar_Students.csv")
NOTE = os.path.join(PROJECT_ROOT, "data", "Grade_Thapar_Students_NOTE.txt")


def main():
    if not os.path.exists(SRC):
        print("ERROR: source dataset not found:", SRC)
        sys.exit(1)

    df = pd.read_csv(SRC, na_values=["NA"])

    keep = {}          # new_thapar_col -> source_col
    for code, _name, _sem, src in FEATURE_MAP:
        keep[code] = src
    for code, _name, _field, src in TARGET_MAP:
        keep[code] = src

    # Validate sources exist
    missing = [src for src in keep.values() if src not in df.columns]
    if missing:
        print("ERROR: these source columns are missing in the CSV:", missing)
        sys.exit(1)

    out = pd.DataFrame()
    out["Year of enrolment"] = df["Year of enrolment"]
    out["ID"] = df["ID"]
    for new_col, src in keep.items():
        out[new_col] = df[src]

    out.to_csv(OUT, index=False)

    with open(NOTE, "w", encoding="utf-8") as f:
        f.write(
            "Grade_Thapar_Students.csv — DISCLOSURE\n"
            "=====================================\n"
            "This file is a RELABELED copy of Grade_CS_Students.csv (335 real\n"
            "students). The grade values are the original students' real grades;\n"
            "only the column headers were renamed to Thapar B.E.(CSE) 2025 course\n"
            "codes (see portal/thapar_map.py).\n\n"
            "It is a demonstration stand-in dataset, NOT real Thapar student data.\n"
            f"Features: {len(FEATURE_MAP)} core courses. Targets: {len(TARGET_MAP)} electives.\n"
        )

    print("Wrote:", OUT)
    print(f"  rows: {len(out)}  features: {len(FEATURE_MAP)}  targets: {len(TARGET_MAP)}")
    print("Wrote disclosure note:", NOTE)


if __name__ == "__main__":
    main()
