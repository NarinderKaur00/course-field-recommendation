"""Print the benchmark results, read back out of the ZenML artifact store."""
import collections

from zenml.client import Client

METRICS = ["accuracy", "balanced_acc", "precision", "recall", "f1_weighted",
           "f1_macro", "cohen_kappa", "mcc"]
HEADINGS = {"accuracy": "Acc", "balanced_acc": "BalAcc", "precision": "Prec",
            "recall": "Rec", "f1_weighted": "F1-w", "f1_macro": "F1-m",
            "cohen_kappa": "Kappa", "mcc": "MCC"}


def load_latest():
    """{target: {model: {metric: value}}} from the newest benchmark run."""
    for run in Client().list_pipeline_runs(size=100).items:
        if run.pipeline.name != "benchmark_pipeline":
            continue
        for step_name, step in run.steps.items():
            if not step_name.startswith("evaluate"):
                continue
            for _, versions in step.outputs.items():
                data = versions[0].load()
                if isinstance(data, dict) and data:
                    return data, run.created
    return None, None


def rule(n):
    print("-" * n)


def main():
    results, created = load_latest()
    if not results:
        print("No benchmark run found. Run:  python run_benchmark_pipeline.py")
        return

    models = list(next(iter(results.values())).keys())
    targets = list(results)

    # ---- 1. Overall leaderboard, averaged across all target subjects ----
    print(f"\nBenchmark run: {created}")
    print(f"{len(models)} models x {len(targets)} target subjects\n")

    print("=" * 78)
    print("  OVERALL LEADERBOARD  (mean across all target subjects)")
    print("=" * 78)
    header = f"{'Model':<14}" + "".join(f"{HEADINGS[m]:>9}" for m in METRICS)
    print(header)
    rule(len(header))

    means = {}
    for model in models:
        means[model] = {
            metric: sum(results[t][model][metric] for t in targets) / len(targets)
            for metric in METRICS
        }

    for model in sorted(models, key=lambda m: means[m]["accuracy"], reverse=True):
        print(f"{model:<14}" + "".join(f"{means[model][m]:>9.4f}" for m in METRICS))
    rule(len(header))

    best = max(models, key=lambda m: means[m]["accuracy"])
    print(f"\nBest overall: {best}  "
          f"(accuracy {means[best]['accuracy']:.4f}, F1-w {means[best]['f1_weighted']:.4f})\n")

    # ---- 2. Per-subject accuracy for every model ----
    print("=" * 78)
    print("  PER-SUBJECT ACCURACY")
    print("=" * 78)
    header = f"{'Subject':<10}" + "".join(f"{m[:9]:>11}" for m in models)
    print(header)
    rule(len(header))
    for target in targets:
        line = f"{target:<10}"
        for model in models:
            line += f"{results[target][model]['accuracy']:>11.4f}"
        print(line)
    rule(len(header))
    line = f"{'MEAN':<10}"
    for model in models:
        line += f"{means[model]['accuracy']:>11.4f}"
    print(line)

    # ---- 3. Which model wins each subject ----
    print("\n" + "=" * 78)
    print("  BEST MODEL PER SUBJECT")
    print("=" * 78)
    wins = collections.Counter()
    for target in targets:
        winner = max(models, key=lambda m: results[target][m]["accuracy"])
        wins[winner] += 1
        print(f"  {target:<10} {winner:<14} {results[target][winner]['accuracy']:.4f}")
    print()
    print("  Wins per model:")
    for model, n in wins.most_common():
        print(f"    {model:<14} {n:>2}  {'#' * n}")

    # ---- 4. Hardest and easiest subjects ----
    print("\n" + "=" * 78)
    print("  SUBJECT DIFFICULTY  (mean accuracy across all models)")
    print("=" * 78)
    by_target = {
        t: sum(results[t][m]["accuracy"] for m in models) / len(models)
        for t in targets
    }
    for target, value in sorted(by_target.items(), key=lambda kv: kv[1], reverse=True):
        bar = "#" * int(value * 40)
        print(f"  {target:<10} {value:.4f}  {bar}")
    print()


main()
