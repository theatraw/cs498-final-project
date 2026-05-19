import pandas as pd
from pathlib import Path

files = sorted(Path("results").glob("job_*.csv"))
df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
df.to_csv("satcomp2023_200_timeout150_cluster.csv", index=False)
print(df)
