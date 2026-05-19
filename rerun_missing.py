from pathlib import Path
import pandas as pd

from bulk_parallel_cluster import run_external_solver

TIMEOUT = 300

missing_jobs = [
    ("maplesat", "BZ2File_write_11.cnf"),
    ("cadical", "PRP_30_41.cnf"),
    ("cadical", "SC23_Timetable_C_481_E_49_Cl_32_D_6_T_50.cnf"),
    ("cadical", "TableSymModel_output_8_4_8.bul_.dimacs.cnf"),
    ("maplesat", "tseitin_grid_n100_m100.cnf"),
]

solvers = {
  "cadical": "/Users/theaat2/Gurobi/final-project/cadical/build/cadical",
  "glucose": "/Users/theaat2/Gurobi/final-project/glucose/simp/glucose",
  "maplesat": "/Users/theaat2/Gurobi/final-project/maplesat/simp/maplesat_static"
}

rows = []

for solver, instance in missing_jobs:
    cnf = Path("benchmarks") / instance
    exe = solvers[solver]

    print(f"Running {solver} on {instance}")
    row = run_external_solver(solver, exe, cnf)
    rows.append(row)
    print(row["status"], row["runtime_sec"])

pd.DataFrame(rows).to_csv("rerun_missing_results.csv", index=False)
print("Saved rerun_missing_results.csv")
