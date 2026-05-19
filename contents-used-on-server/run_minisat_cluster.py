import os
import random
import time
from pathlib import Path

import pandas as pd
from pysat.formula import CNF
from pysat.solvers import Minisat22


BENCHMARK_DIR = Path("benchmarks")
N_INSTANCES = 5
TIMEOUT = 300  # mostly documented; Slurm enforces walltime here


def run_pysat_minisat(cnf_path):
    start = time.time()

    try:
        load_start = time.time()
        cnf = CNF(from_file=str(cnf_path))
        load_time = time.time() - load_start

        init_start = time.time()
        solver = Minisat22(bootstrap_with=cnf.clauses)
        init_time = time.time() - init_start

        solve_start = time.time()
        sat = solver.solve()
        solve_time = time.time() - solve_start

        stats = solver.accum_stats()
        solver.delete()

        total_time = time.time() - start

        return {
            "solver": "pysat_minisat22",
            "instance": cnf_path.name,
            "path": str(cnf_path),
            "status": "SAT" if sat else "UNSAT",
            "runtime_sec": total_time,
            "load_time_sec": load_time,
            "solver_init_time_sec": init_time,
            "solve_time_sec": solve_time,
            "returncode": 0,
            "timeout": False,
            "killed": False,
            "conflicts": stats.get("conflicts"),
            "decisions": stats.get("decisions"),
            "propagations": stats.get("propagations"),
            "restarts": stats.get("restarts"),
            "variables": cnf.nv,
            "clauses": len(cnf.clauses),
        }

    except Exception as e:
        return {
            "solver": "pysat_minisat22",
            "instance": cnf_path.name,
            "path": str(cnf_path),
            "status": f"ERROR: {type(e).__name__}: {e}",
            "runtime_sec": time.time() - start,
            "returncode": None,
            "timeout": False,
            "killed": False,
        }


def main():
    cnfs = sorted(BENCHMARK_DIR.rglob("*.cnf"))

    random.seed(23456823)
    random.shuffle(cnfs)

    cnfs = cnfs[:N_INSTANCES]

    task_id = int(os.environ["SLURM_ARRAY_TASK_ID"])

    if task_id < 0 or task_id >= len(cnfs):
        raise IndexError(f"Task ID {task_id} out of range for {len(cnfs)} instances")

    cnf = cnfs[task_id]

    print(f"Task {task_id}/{len(cnfs)-1}")
    print(f"Running PySAT MiniSAT22 on {cnf}")

    row = run_pysat_minisat(cnf)

    out_dir = Path("results_minisat")
    out_dir.mkdir(exist_ok=True)

    out_path = out_dir / f"job_{task_id:05d}.csv"
    pd.DataFrame([row]).to_csv(out_path, index=False)

    print(f"Done: {row['status']} {row['runtime_sec']:.2f}s")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
