import pandas as pd
import itertools

df = pd.read_csv("satcomp2023_400_timeout300.csv")

print(df.shape)
print(df["status"].value_counts(dropna=False))
print(df.groupby("solver")["status"].value_counts())
print(df["instance"].nunique())

instances = sorted(df["instance"].unique())
solvers = sorted(df["solver"].unique())

expected = pd.DataFrame(
    itertools.product(instances, solvers),
    columns=["instance", "solver"]
)

missing = expected.merge(
    df[["instance", "solver"]],
    on=["instance", "solver"],
    how="left",
    indicator=True
)

missing = missing[missing["_merge"] == "left_only"]

print(missing)
print("Missing:", len(missing))
