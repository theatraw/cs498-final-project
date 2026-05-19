import pandas as pd

MAIN_CSV = "sat400_complete.csv"
BASELINE_CSV = "final-project-copy/sat_baseline400.csv"

OUTPUT_CSV = "sat_complete_with_minisat.csv"

# load
main_df = pd.read_csv(MAIN_CSV)
baseline_df = pd.read_csv(BASELINE_CSV)

print("Main shape:", main_df.shape)
print("Baseline shape:", baseline_df.shape)

# combine
combined = pd.concat(
    [main_df, baseline_df],
    ignore_index=True
)

print("Combined shape:", combined.shape)

# quick sanity checks
print("\n=== Solver counts ===")
print(combined["solver"].value_counts())

print("\n=== Status counts ===")
print(combined["status"].value_counts())

# save
combined.to_csv(OUTPUT_CSV, index=False)

print(f"\nSaved {OUTPUT_CSV}")
