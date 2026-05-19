import pandas as pd
import numpy as np

OUTPUT_CSV = "sat400_with_proxies.csv"

RESULTS_CSV = "sat400_complete.csv"
CATEGORY_CSV = "sat400_results_categorized.csv"

# load
df = pd.read_csv(RESULTS_CSV)
cats = pd.read_csv(CATEGORY_CSV)

# merge categories into results
df = df.merge(cats, on="instance", how="left")

# avoid divide-by-zero issues
def safe_div(a, b):
    return np.where(
        (b == 0) | (pd.isna(b)),
        np.nan,
        a / b
    )

# ensure numeric
numeric_cols = [
    "runtime_sec",
    "conflicts",
    "decisions",
    "propagations",
    "restarts",
    "learned_clauses",
    "removed_clauses",
    "reduced_clauses",
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

#
# Branching / search proxies
#

df["decisions_per_conflict"] = safe_div(
    df["decisions"],
    df["conflicts"]
)

df["conflicts_per_decision"] = safe_div(
    df["conflicts"],
    df["decisions"]
)

df["decisions_per_second"] = safe_div(
    df["decisions"],
    df["runtime_sec"]
)

#
# Restart behavior proxies
#

df["restarts_per_conflict"] = safe_div(
    df["restarts"],
    df["conflicts"]
)

df["conflicts_per_restart"] = safe_div(
    df["conflicts"],
    df["restarts"]
)

df["restarts_per_second"] = safe_div(
    df["restarts"],
    df["runtime_sec"]
)

#
# Clause learning / deletion proxies
#

df["learned_per_conflict"] = safe_div(
    df["learned_clauses"],
    df["conflicts"]
)

df["removed_per_conflict"] = safe_div(
    df["removed_clauses"],
    df["conflicts"]
)

df["reduced_per_conflict"] = safe_div(
    df["reduced_clauses"],
    df["conflicts"]
)

#
# Propagation behavior proxies
#

df["propagations_per_conflict"] = safe_div(
    df["propagations"],
    df["conflicts"]
)

df["propagations_per_decision"] = safe_div(
    df["propagations"],
    df["decisions"]
)

#
# Save
#

df.to_csv(OUTPUT_CSV, index=False)

print(f"Saved {OUTPUT_CSV}")
print(df.shape)

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

print("\nAdded proxy columns:")
for c in proxy_cols:
    print("-", c)
