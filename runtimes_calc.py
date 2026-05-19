import pandas as pd

df = pd.read_csv("sat400_complete.csv")

# only solved runs
solved = df[df["status"].isin(["SAT", "UNSAT"])].copy()

# bins in seconds
bins = [0, 60, 120, 180, 240, 300]

labels = [
    "0-1 min",
    "1-2 min",
    "2-3 min",
    "3-4 min",
    "4-5 min",
]

solved["runtime_bucket"] = pd.cut(
    solved["runtime_sec"],
    bins=bins,
    labels=labels,
    include_lowest=True
)

# overall counts
print("\n=== Overall solved runtime distribution ===")
print(
    solved["runtime_bucket"]
    .value_counts()
    .sort_index()
)

# by solver
print("\n=== Runtime distribution by solver ===")

runtime_dist = (
    solved
    .groupby(["solver", "runtime_bucket"])
    .size()
    .unstack(fill_value=0)
)

print(runtime_dist)
