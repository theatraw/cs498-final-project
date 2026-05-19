import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


RESULTS_CSV = "sat400_complete.csv"
CATEGORY_CSV = "sat400_results_categorized.csv"

OUT_DIR = Path("figures")

# load
df = pd.read_csv(RESULTS_CSV)
cats = pd.read_csv(CATEGORY_CSV)

# merge categories into results
df = df.merge(cats, on="instance", how="left")


# solved only for mechanism comparisons
df["solved"] = df["status"].isin(["SAT", "UNSAT"])
solved = df[df["solved"]].copy()

# derived metrics
solved["prop_per_conflict"] = solved["propagations"] / solved["conflicts"]
solved["decisions_per_conflict"] = solved["decisions"] / solved["conflicts"]
solved["restarts_per_conflict"] = solved["restarts"] / solved["conflicts"]

# avoid inf/nan issues
metric_cols = [
    "conflicts",
    "decisions",
    "propagations",
    "restarts",
    "prop_per_conflict",
    "decisions_per_conflict",
    "restarts_per_conflict",
]

for col in metric_cols:
    solved[col] = pd.to_numeric(solved[col], errors="coerce")

summary = (
    solved
    .groupby("solver")[metric_cols]
    .median()
    .reset_index()
)

print("\n=== Median mechanism metrics on solved instances ===")
print(summary)

summary.to_csv("mechanism_summary_by_solver.csv", index=False)

# one plot per metric
for metric in metric_cols:
    plot_df = summary[["solver", metric]].dropna()

    plt.figure(figsize=(7, 5))
    plt.bar(plot_df["solver"], plot_df[metric])

    plt.xlabel("Solver")
    plt.ylabel(metric)
    plt.title(f"Median {metric} on Solved Instances")
    plt.grid(axis="y", alpha=0.3)

    plt.savefig(
        OUT_DIR / f"mechanism_{metric}.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.show()

# SAT vs UNSAT mechanism comparison
sat_unsat_summary = (
    solved
    .groupby(["status", "solver"])[metric_cols]
    .median()
    .reset_index()
)

sat_unsat_summary.to_csv("mechanism_summary_sat_unsat.csv", index=False)

for metric in ["conflicts", "propagations", "restarts"]:
    pivot = sat_unsat_summary.pivot(
        index="solver",
        columns="status",
        values=metric
    )

    pivot.plot(kind="bar", figsize=(8, 5))

    plt.xlabel("Solver")
    plt.ylabel(metric)
    plt.title(f"Median {metric}: SAT vs UNSAT")
    plt.grid(axis="y", alpha=0.3)
    plt.legend(title="Status")

    plt.savefig(
        OUT_DIR / f"mechanism_{metric}_sat_vs_unsat.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.show()

# Category-level comparison
if "category" in solved.columns:
    category_summary = (
        solved
        .groupby(["category", "solver"])[
            ["conflicts", "propagations", "restarts"]
        ]
        .median()
        .reset_index()
    )

    category_summary.to_csv("mechanism_summary_by_category.csv", index=False)

    for metric in ["conflicts", "propagations", "restarts"]:
        pivot = category_summary.pivot(
            index="category",
            columns="solver",
            values=metric
        )

        pivot.plot(kind="bar", figsize=(9, 5))

        plt.xlabel("Category")
        plt.ylabel(metric)
        plt.title(f"Median {metric} by Benchmark Category")
        plt.grid(axis="y", alpha=0.3)
        plt.legend(title="Solver")

        plt.savefig(
            OUT_DIR / f"mechanism_{metric}_by_category.png",
            dpi=300,
            bbox_inches="tight"
        )
        plt.show()
