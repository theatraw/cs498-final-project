import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS_CSV = "sat_complete_with_minisat.csv"
CATEGORY_CSV = "sat400_results_categorized.csv"

OUT_DIR = Path("boxplots_metrics_ACTUALLYFINAL")
OUT_DIR.mkdir(exist_ok=True)

# load
df = pd.read_csv(RESULTS_CSV)
cats = pd.read_csv(CATEGORY_CSV)

# merge categories into results
df = df.merge(cats, on="instance", how="left")

# Use completed runs for mechanism metrics
df = df[df["status"].isin(["SAT", "UNSAT"])].copy()

numeric_cols = ["conflicts", "decisions", "restarts", "propagations", "runtime_sec"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

def safe_div(a, b):
    return np.where((b == 0) | pd.isna(b), np.nan, a / b)

df["conflicts_per_decision"] = safe_div(df["conflicts"], df["decisions"])
df["conflicts_per_restart"] = safe_div(df["conflicts"], df["restarts"])
df["propagations_per_decision"] = safe_div(df["propagations"], df["decisions"])

metrics = [
    "conflicts_per_decision",
    "conflicts_per_restart",
    "propagations_per_decision",
]

subset_defs = {
    "total": df,
    "SAT": df[df["status"] == "SAT"],
    "UNSAT": df[df["status"] == "UNSAT"],
    "crafted": df[df["category"] == "crafted"],
    "random": df[df["category"] == "random"],
    "industrial": df[df["category"] == "industrial"],
}

subsets = list(subset_defs.keys())
solvers = ["cadical", "glucose", "maplesat", "minisat"]
solvers = [s for s in solvers if s in df["solver"].unique()]

colors = {
    "cadical": "tab:blue",
    "glucose": "tab:orange",
    "maplesat": "tab:green",
    "minisat": "tab:red",
}

for metric in metrics:
    fig, ax = plt.subplots(figsize=(12, 6))

    width = 0.16
    centers = np.arange(len(subsets))

    for i, solver in enumerate(solvers):
        data = []

        for subset in subsets:
            sub = subset_defs[subset]
            vals = sub[sub["solver"] == solver][metric].dropna().values
            data.append(vals)

        positions = centers + (i - (len(solvers) - 1) / 2) * width

        bp = ax.boxplot(
            data,
            positions=positions,
            widths=width * 0.9,
            patch_artist=True,
            showfliers=False,
        )

        for box in bp["boxes"]:
            box.set_facecolor(colors.get(solver, "gray"))
            box.set_alpha(0.65)

        for median in bp["medians"]:
            median.set_color("black")

    ax.set_xticks(centers)
    ax.set_xticklabels(subsets)

    ax.set_xlabel("Instance subset")
    ax.set_ylabel(metric)
    ax.set_title(f"{metric} by instance subset and solver")
    ax.grid(axis="y", alpha=0.3)

    handles = [
        plt.Line2D([0], [0], color=colors.get(s, "gray"), lw=8, label=s)
        for s in solvers
    ]
    ax.legend(handles=handles, title="Solver")

    out_path = OUT_DIR / f"grouped_boxplot_{metric}.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.show()

    print(f"Saved {out_path}")
