import json
import re
import subprocess
import time
from pathlib import Path
import pandas as pd
from pysat.formula import CNF
from pysat.solvers import Minisat22
import random
import os

TIMEOUT = 300
BENCHMARK_DIR = Path("benchmarks")   # change if needed
N_INSTANCES = 400

def detect_status(output):
    if "UNSATISFIABLE" in output:
        return "UNSAT"
    if "SATISFIABLE" in output:
        return "SAT"
    return "UNKNOWN"


def parse_minisat(output):
    def grab_int(pattern):
        m = re.search(pattern, output, re.MULTILINE)
        return int(m.group(1).replace(",", "")) if m else None

    def grab_float(pattern):
        m = re.search(pattern, output, re.MULTILINE)
        return float(m.group(1).replace(",", "")) if m else None

    if re.search(r"^UNSATISFIABLE", output, re.MULTILINE):
        status = "UNSAT"
    elif re.search(r"^SATISFIABLE", output, re.MULTILINE):
        status = "SAT"
    elif re.search(r"^INDETERMINATE", output, re.MULTILINE):
        status = "INDETERMINATE"
    else:
        status = "UNKNOWN"

    return {
        "status": status,
        "variables": grab_int(r"^\|\s+Number of variables:\s+([0-9,]+)"),
        "clauses": grab_int(r"^\|\s+Number of clauses:\s+([0-9,]+)"),
        "restarts": grab_int(r"^restarts\s+:\s+([0-9,]+)"),
        "conflicts": grab_int(r"^conflicts\s+:\s+([0-9,]+)"),
        "decisions": grab_int(r"^decisions\s+:\s+([0-9,]+)"),
        "propagations": grab_int(r"^propagations\s+:\s+([0-9,]+)"),
        "conflict_literals": grab_int(r"^conflict literals\s+:\s+([0-9,]+)"),
        "memory_reported_mb": grab_float(r"^Memory used\s+:\s+([0-9.]+)\s+MB"),
        "cpu_time_reported": grab_float(r"^CPU time\s+:\s+([0-9.]+)"),
    }

def parse_by_solver(name, output):
    name_lower = name.lower()

    if "minisat" in name_lower:
        return parse_minisat(output)

    return {"status": detect_status(output)}


def empty_stats_row():
    return {
        "conflicts": None,
        "decisions": None,
        "propagations": None,
        "restarts": None,
        "variables": None,
        "clauses": None,
        "cpu_time_reported": None,
    }

def run_external_solver(name, exe, cnf_path):
    start = time.time()

    try:
        proc = subprocess.run(
            [exe, str(cnf_path)],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )

        elapsed = time.time() - start
        output = proc.stdout + "\n" + proc.stderr
        parsed = parse_by_solver(name, output)

        killed = proc.returncode == -9
        status = "KILLED" if killed else parsed.get("status", detect_status(output))

        row = {
            "solver": name,
            "instance": cnf_path.name,
            "path": str(cnf_path),
            "status": status,
            "runtime_sec": elapsed,
            "returncode": proc.returncode,
            "timeout": False,
            "killed": killed,
        }

        row.update(empty_stats_row())
        row.update(parsed)
        row["status"] = status
        row["killed"] = killed

        return row

    except subprocess.TimeoutExpired as e:
        output = ""

        if e.stdout:
            output += e.stdout if isinstance(e.stdout, str) else e.stdout.decode(errors="ignore")
        if e.stderr:
            output += "\n"
            output += e.stderr if isinstance(e.stderr, str) else e.stderr.decode(errors="ignore")

        parsed = parse_by_solver(name, output) if output else {}

        row = {
            "solver": name,
            "instance": cnf_path.name,
            "path": str(cnf_path),
            "status": "TIMEOUT",
            "runtime_sec": TIMEOUT,
            "returncode": None,
            "timeout": True,
            "killed": False,
        }

        row.update(empty_stats_row())
        row.update(parsed)
        row["status"] = "TIMEOUT"
        row["killed"] = False

        return row


def run_one_job(job):
    name, exe, cnf = job
    return run_external_solver(name, exe, cnf)

def build_jobs():
    
    solvers = {
        "minisat": "/u/ttraw/minisat-install/bin/minisat",
    }

    cnfs = sorted(BENCHMARK_DIR.rglob("*.cnf"))

    random.seed(23456823)
    random.shuffle(cnfs)

    if N_INSTANCES is not None:
        cnfs = cnfs[:N_INSTANCES]

    jobs = [
        (name, exe, cnf)
        for cnf in cnfs
        for name, exe in solvers.items()
    ]

    return jobs

def main():
    jobs = build_jobs()

    if "SLURM_ARRAY_TASK_ID" not in os.environ:
        raise RuntimeError(
            "SLURM_ARRAY_TASK_ID not found. "
            "This cluster version should be run as a Slurm job array."
        )

    task_id = int(os.environ["SLURM_ARRAY_TASK_ID"])

    if task_id < 0 or task_id >= len(jobs):
        raise IndexError(f"Task ID {task_id} out of range for {len(jobs)} jobs")

    name, exe, cnf = jobs[task_id]

    print(f"Task {task_id}/{len(jobs)-1}")
    print(f"Solver: {name}")
    print(f"CNF: {cnf}")

    row = run_external_solver(name, exe, cnf)

    results_dir = Path("results_minisat")
    results_dir.mkdir(exist_ok=True)

    out_path = results_dir / f"job_{task_id:05d}.csv"

    pd.DataFrame([row]).to_csv(out_path, index=False)

    print(
        f"Done: {row['solver']} {row['instance']} "
        f"{row['status']} {row['runtime_sec']:.2f}s"
    )
    print(f"Saved {out_path}")

if __name__ == "__main__":
    main()
