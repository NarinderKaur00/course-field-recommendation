"""Print a model comparison table, read back out of the ZenML artifact store.

Only classification pipelines appear here (XGB / RF / MLP). The SVM pipeline is
a linear-regression baseline scored with MSE, so it has no accuracy/F1 to compare.
"""
import collections

from zenml.client import Client


def collect():
    """Return {subject: {(model, metric): value}} for the newest run of each pipeline."""
    rows = collections.defaultdict(dict)
    seen = set()

    # list_pipeline_runs returns newest first, so the first run we see for a
    # given pipeline is the one to report.
    for run in Client().list_pipeline_runs(size=100).items:
        model = run.pipeline.name.replace("_pipeline", "")
        if model in seen:
            continue

        found = False
        for step_name, step in run.steps.items():
            if not step_name.startswith("evaluate"):
                continue
            for _, versions in step.outputs.items():
                data = versions[0].load()
                if not isinstance(data, dict) or not data:
                    continue
                for key, value in data.items():
                    subject, metric = key.rsplit("_", 1)
                    rows[subject][(model, metric)] = value
                    found = True
        if found:
            seen.add(model)

    return rows


def main():
    rows = collect()
    if not rows:
        print("No evaluation results found. Run the pipelines first.")
        return

    models = sorted({m for r in rows.values() for (m, _) in r})
    header = f"{'Subject':<10}" + "".join(
        f"{m + ' acc':>12}{m + ' f1':>12}" for m in models)
    rule = "-" * len(header)

    print(header)
    print(rule)

    totals = collections.defaultdict(list)
    for subject in sorted(rows):
        line = f"{subject:<10}"
        for model in models:
            for metric in ("accuracy", "f1"):
                value = rows[subject].get((model, metric))
                line += f"{value:>12.4f}" if value is not None else f"{'-':>12}"
                if value is not None:
                    totals[(model, metric)].append(value)
        print(line)

    print(rule)
    line = f"{'MEAN':<10}"
    for model in models:
        for metric in ("accuracy", "f1"):
            values = totals[(model, metric)]
            line += f"{sum(values) / len(values):>12.4f}" if values else f"{'-':>12}"
    print(line)


main()
