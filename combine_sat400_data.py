import pandas as pd

df = pd.read_csv("satcomp2023_400_timeout300.csv")
rerun = pd.read_csv("rerun_missing_results.csv")

complete = pd.concat([df, rerun], ignore_index=True)

complete = complete.drop_duplicates(
    subset=["solver", "instance"],
    keep="last"
)

print(complete.shape)
print(complete["status"].value_counts())
print(complete.groupby("solver")["status"].value_counts())

complete.to_csv("sat400_complete.csv", index=False)

print("Saved sat_complete.csv")
