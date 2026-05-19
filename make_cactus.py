import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS_CSV = "sat_complete_with_minisat.csv"
OUT_DIR = Path("figures")

df = pd.read_csv(RESULTS_CSV)

df["solved"] = df["status"].isin(["SAT", "UNSAT"])

plt.figure(figsize=(8, 6))

for solver, subdf in df.groupby("solver"):
    solved_times = sorted(subdf.loc[subdf["solved"], "runtime_sec"])

    x = range(1, len(solved_times) + 1)
    y = solved_times

    plt.plot(x, y, label=f"{solver} ({len(solved_times)} solved)")

plt.xlabel("Instances solved")
plt.ylabel("Runtime (seconds)")
plt.title("Cactus Plot: SAT Competition 2023 Main Track")
plt.legend()
plt.grid(True, alpha=0.3)

plt.savefig(OUT_DIR / "cactus_overall.png", dpi=300, bbox_inches="tight")
plt.show()
