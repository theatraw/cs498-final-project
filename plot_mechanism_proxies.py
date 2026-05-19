import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

INPUT_CSV = "sat400_with_proxies.csv"
OUT_DIR = Path("figures")
OUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(INPUT_CSV)

# Use only completed SAT/UNSAT runs for mechanism metrics
df = df[df["status"].isin(["SAT", "UNSAT"])].copy()

proxy_cols = [
    "decisions_per_conflict",
    "conflicts_per_decision",
    "decisions_per_second",
    "restarts_per_conflict",
    "conflicts_per_restart",
    "restarts_per_second",
    "learned_per_conflict",
    "removed_per_conflict",
    "reduced_per_conflict",
    "propagations_per_conflict",
    "propagations_per_decision",
]

# -------------------------
# Boxplots by solver
# -------------------------

for col in proxy_cols:
    plot_df = df[["solver", col]].dropna()

    plt.figure(figsize=(8, 5))

    plot_df.boxplot(
        column=col,
        by="solver",
        grid=False
    )

    plt.title(f"{col} by Solver")
    plt.suptitle("")
    plt.xlabel("Solver")
    plt.ylabel(col)
    plt.grid(axis="y", alpha=0.3)

    plt.savefig(OUT_DIR / f"boxplot_{col}_by_solver.png", dpi=300, bbox_inches="tight")
    plt.show()

# -------------------------
# Boxplots by category + solver
# -------------------------

for col in proxy_cols:
    for category in ["crafted", "industrial", "random"]:
        plot_df = df[df["category"] == category][["solver", col]].dropna()

        if plot_df.empty:
            continue

        plt.figure(figsize=(8, 5))

        plot_df.boxplot(
            column=col,
            by="solver",
            grid=False
        )

        plt.title(f"{col} by Solver — {category}")
        plt.suptitle("")
        plt.xlabel("Solver")
        plt.ylabel(col)
        plt.grid(axis="y", alpha=0.3)

        plt.savefig(
            OUT_DIR / f"boxplot_{col}_by_solver_{category}.png",
            dpi=300,
            bbox_inches="tight"
        )
        plt.show()

# -------------------------
# Heatmap of median proxy values
# solver x proxy
# -------------------------

summary = df.groupby("solver")[proxy_cols].median()

# Normalize each proxy column so magnitudes are comparable
norm_summary = summary.copy()
for col in proxy_cols:
    min_val = norm_summary[col].min()
    max_val = norm_summary[col].max()

    if pd.notna(min_val) and pd.notna(max_val) and max_val != min_val:
        norm_summary[col] = (norm_summary[col] - min_val) / (max_val - min_val)

plt.figure(figsize=(12, 5))
plt.imshow(norm_summary, aspect="auto")

plt.xticks(range(len(proxy_cols)), proxy_cols, rotation=45, ha="right")
plt.yticks(range(len(norm_summary.index)), norm_summary.index)

plt.colorbar(label="Normalized median value")
plt.title("Mechanism Proxy Heatmap by Solver")

plt.savefig(OUT_DIR / "heatmap_mechanism_proxies_by_solver.png", dpi=300, bbox_inches="tight")
plt.show()

# -------------------------
# Heatmap by category + solver
# -------------------------

category_summary = (
    df.groupby(["category", "solver"])[proxy_cols]
    .median()
)

norm_category_summary = category_summary.copy()
for col in proxy_cols:
    min_val = norm_category_summary[col].min()
    max_val = norm_category_summary[col].max()

    if pd.notna(min_val) and pd.notna(max_val) and max_val != min_val:
        norm_category_summary[col] = (
            (norm_category_summary[col] - min_val) / (max_val - min_val)
        )

plt.figure(figsize=(12, 8))
plt.imshow(norm_category_summary, aspect="auto")

plt.xticks(range(len(proxy_cols)), proxy_cols, rotation=45, ha="right")
plt.yticks(
    range(len(norm_category_summary.index)),
    [f"{cat} / {solver}" for cat, solver in norm_category_summary.index]
)

plt.colorbar(label="Normalized median value")
plt.title("Mechanism Proxy Heatmap by Category and Solver")

plt.savefig(
    OUT_DIR / "heatmap_mechanism_proxies_by_category_solver.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

# Save raw summaries too
summary.to_csv("mechanism_proxy_medians_by_solver.csv")
category_summary.to_csv("mechanism_proxy_medians_by_category_solver.csv")

print("Saved plots to figures/")
print("Saved mechanism_proxy_medians_by_solver.csv")
print("Saved mechanism_proxy_medians_by_category_solver.csv")
