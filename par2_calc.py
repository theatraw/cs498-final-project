import pandas as pd

TIMEOUT = 300

df = pd.read_csv("sat_complete_with_minisat.csv")

# solved?
df["solved"] = df["status"].isin(["SAT", "UNSAT"])

# PAR-2 runtime
df["par2_runtime"] = df["runtime_sec"]

df.loc[~df["solved"], "par2_runtime"] = 2 * TIMEOUT

# overall PAR-2
par2 = (
    df.groupby("solver")["par2_runtime"]
      .mean()
      .sort_values()
)

print("\n=== Overall PAR-2 ===")
print(par2)

# solved counts
print("\n=== Solved Counts ===")
print(df.groupby("solver")["solved"].sum())



df = df.merge(
    pd.read_csv("sat400_results_categorized.csv"),
    on="instance",
    how="left"
)

category_par2 = (
    df.groupby(["category", "solver"])["par2_runtime"]
      .mean()
      .unstack()
)

print(category_par2)

truth = (
    df[df["status"].isin(["SAT", "UNSAT"])]
      .groupby("instance")["status"]
      .first()
      .rename("instance_status")
)

df = df.merge(truth, on="instance", how="left")

print("\n=== PAR-2 by SAT/UNSAT ===")
sat_par2 = (
    df.groupby(["instance_status", "solver"])["par2_runtime"]
      .mean()
      .unstack()
)
print(sat_par2)
