import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS_CSV = "sat_complete_with_minisat.csv"
OUT_DIR = Path("figures")

df = pd.read_csv(RESULTS_CSV)
df["solved"] = df["status"].isin(["SAT", "UNSAT"])

for outcome in ["SAT", "UNSAT"]:
    sub = df[df["status"] == outcome]

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
    plt.title(f"Cactus Plot: {outcome} Instances")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(OUT_DIR / f"cactus_{outcome.lower()}.png", dpi=300, bbox_inches="tight")
    plt.show()
