"""Generate additional SYNTHETIC student records for experimentation.

The records are NOT real students. They are sampled from a Gaussian copula
fitted to the real data, which reproduces each subject's mark distribution and
the correlations between subjects, but invents the individuals.

Synthetic rows are written with ID 'SYNnnn' and 'SYNTHETIC' in the year column
so they can always be told apart from the 335 real students.

Usage:
    python scripts/generate_synthetic_students.py [n_new] [output_path]
"""
import sys

import numpy as np
import pandas as pd
from scipy import stats

REAL_PATH = "./data/Grade_CS_Students.csv"
META = ["Year of enrolment", "ID"]
SEED = 42


def fit_and_sample(marks: pd.DataFrame, n_new: int, rng) -> pd.DataFrame:
    """Sample n_new rows from a Gaussian copula fitted to `marks`."""
    n_real, n_col = marks.shape

    # 1. Marginals -> uniform via ranks, then -> standard normal.
    ranks = marks.rank(method="average").to_numpy() / (n_real + 1)
    normal = stats.norm.ppf(ranks)

    # 2. Correlation of the normal scores, shrunk towards the identity so the
    #    matrix stays positive-definite with 66 columns and only 335 rows.
    corr = np.corrcoef(normal, rowvar=False)
    corr = np.nan_to_num(corr, nan=0.0)
    corr = 0.9 * corr + 0.1 * np.eye(n_col)

    # 3. Sample, map back to uniform, then back through the empirical quantiles
    #    so each synthetic column has the same marginal as the real one.
    sample = rng.multivariate_normal(np.zeros(n_col), corr, size=n_new)
    uniform = stats.norm.cdf(sample)

    out = {}
    for i, col in enumerate(marks.columns):
        out[col] = np.quantile(marks[col].to_numpy(), uniform[:, i])
    return pd.DataFrame(out).round().astype(int)


def main():
    n_new = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    out_path = sys.argv[2] if len(sys.argv) > 2 else "./data/Grade_CS_Students_augmented.csv"

    real = pd.read_csv(REAL_PATH, na_values=["NA"])
    subjects = [c for c in real.columns if c not in META]

    marks = real[subjects].apply(pd.to_numeric, errors="coerce")
    marks = marks.fillna(marks.median())

    rng = np.random.default_rng(SEED)
    synthetic = fit_and_sample(marks, n_new, rng)

    # Clip to the observed mark range so nothing impossible is produced.
    synthetic = synthetic.clip(lower=int(marks.min().min()), upper=int(marks.max().max()))

    synthetic.insert(0, "ID", [f"SYN{i + 1:03d}" for i in range(n_new)])
    synthetic.insert(0, "Year of enrolment", "SYNTHETIC")

    combined = pd.concat([real, synthetic], ignore_index=True)
    combined.to_csv(out_path, index=False)

    print(f"Real students      : {len(real)}")
    print(f"Synthetic students : {len(synthetic)}  (ID SYN001..SYN{n_new:03d})")
    print(f"Total              : {len(combined)}")
    print(f"Written to         : {out_path}")
    print()
    print("Marginal check (mean mark per dataset, first 8 subjects):")
    comp = pd.DataFrame({
        "real": marks[subjects].mean(),
        "synthetic": synthetic[subjects].mean(),
    }).head(8).round(2)
    print(comp.to_string())


main()
