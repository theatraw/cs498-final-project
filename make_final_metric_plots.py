import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS_CSV = "sat_complete_with_minisat.csv"
CATEGORY_CSV = "sat400_results_categorized.csv"

OUT_DIR = Path("boxplots_metrics_final")
OUT_DIR.mkdir(exist_ok=True)

# load
df = pd.read_csv(RESULTS_CSV)
cats = pd.read_csv(CATEGORY_CSV)

# merge categories into results
df = df.merge(cats, on="instance", how="left")

# Use completed runs for mechanism metrics
df = df[df["status"].isin(["SAT", "UNSAT"])].copy()

for col in [
    "conflicts",
    "decisions",
    "restarts",
    "removed_clauses",
    "learned_clauses",
    "propagations",
]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

def safe_div(a, b):
    return np.where((b == 0) | pd.isna(b), np.nan, a / b)

df["conflicts_per_decision"] = safe_div(df["conflicts"], df["decisions"])
df["conflicts_per_restart"] = safe_div(df["conflicts"], df["restarts"])
df["removed_per_conflict"] = safe_div(df["removed_clauses"], df["conflicts"])
df["learned_per_conflict"] = safe_div(df["learned_clauses"], df["conflicts"])
df["propagations_per_decision"] = safe_div(df["propagations"], df["decisions"])

metrics = [
    "conflicts_per_decision",
    "conflicts_per_restart",
    "removed_per_conflict",
    "learned_per_conflict",
    "propagations_per_decision",
]

groups = {
    "total": lambda x: x,
    "SAT": lambda x: x[x["status"] == "SAT"],
    "UNSAT": lambda x: x[x["status"] == "UNSAT"],
    "random": lambda x: x[x["category"] == "random"],
    "industrial": lambda x: x[x["category"] == "industrial"],
    "crafted": lambda x: x[x["category"] == "crafted"],
}

solvers = ["cadical", "glucose", "maplesat", "minisat"]
solvers = [s for s in solvers if s in df["solver"].unique()]

group_names = list(groups.keys())

for metric in metrics:
    data = []
    positions = []
    labels = []

    base_gap = len(group_names) + 1

    for i, solver in enumerate(solvers):
        solver_df = df[df["solver"] == solver]

        for j, group_name in enumerate(group_names):
            group_df = groups[group_name](solver_df)
            vals = group_df[metric].dropna().values

            if len(vals) == 0:
                vals = np.array([np.nan])

            data.append(vals)
            positions.append(i * base_gap + j)
            labels.append(group_name)

    plt.figure(figsize=(14, 6))

    plt.boxplot(
        data,
        positions=positions,
        widths=0.6,
        showfliers=False
    )

    # x ticks centered under each solver group
    solver_centers = [
        i * base_gap + (len(group_names) - 1) / 2
        for i in range(len(solvers))
    ]

    plt.xticks(solver_centers, solvers)

    # add small group labels under each box
    ax = plt.gca()
    ymin, ymax = ax.get_ylim()
    y_text = ymin - 0.08 * (ymax - ymin)

    for pos, label in zip(positions, labels):
        ax.text(
            pos,
            y_text,
            label,
            rotation=45,
            ha="right",
            va="top",
            fontsize=8,
            clip_on=False
        )

    plt.subplots_adjust(bottom=0.25)

    plt.xlabel("Solver")
    plt.ylabel(metric)
    plt.title(f"{metric} by Solver and Subset")
    plt.grid(axis="y", alpha=0.3)

    out_path = OUT_DIR / f"boxplot_{metric}_solver_subsets.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.show()

    print(f"Saved {out_path}")
