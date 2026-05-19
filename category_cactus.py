import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS_CSV = "sat_complete_with_minisat.csv"
CATEGORY_CSV = "sat400_results_categorized.csv"

OUT_DIR = Path("figures")

# load
df = pd.read_csv(RESULTS_CSV)
cats = pd.read_csv(CATEGORY_CSV)

# merge categories into results
df = df.merge(cats, on="instance", how="left")

# solved = SAT or UNSAT
df["solved"] = df["status"].isin(["SAT", "UNSAT"])

print(df["category"].value_counts(dropna=False))

# make category cactus plots
for category in ["crafted", "industrial", "random"]:

    sub = df[
        (df["category"] == category) &
        (df["solved"])
    ]

    plt.figure(figsize=(8, 6))

    for solver, sdf in sub.groupby("solver"):

        times = sorted(sdf["runtime_sec"])

        plt.plot(
            range(1, len(times) + 1),
            times,
            label=f"{solver} ({len(times)} solved)"
        )

    plt.xlabel("Instances solved")
    plt.ylabel("Runtime (seconds)")
    plt.title(f"Cactus Plot: {category.capitalize()} Benchmarks")

    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig(
        OUT_DIR / f"cactus_{category}.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
