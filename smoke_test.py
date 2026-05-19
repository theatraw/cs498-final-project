import json
import re
import subprocess
import time
from pathlib import Path
import pandas as pd
from pysat.formula import CNF
from pysat.solvers import Minisat22

TIMEOUT = 10
BENCHMARK_DIR = Path("benchmarks")   # change if needed
N_INSTANCES = 5

def detect_status(output):
    if "UNSATISFIABLE" in output:
        return "UNSAT"
    if "SATISFIABLE" in output:
        return "SAT"
    return "UNKNOWN"

def parse_cadical(output):
    def grab_int(name):
        m = re.search(rf"^c {name}:\s*([0-9,]+)", output, re.MULTILINE)
        return int(m.group(1).replace(",", "")) if m else None

    def grab_float(pattern):
        m = re.search(pattern, output, re.MULTILINE)
        return float(m.group(1).replace(",", "")) if m else None

    if re.search(r"^s UNSATISFIABLE", output, re.MULTILINE):
        status = "UNSAT"
    elif re.search(r"^s SATISFIABLE", output, re.MULTILINE):
        status = "SAT"
    else:
        status = "UNKNOWN"

    m_exit = re.search(r"^c exit\s+([0-9]+)", output, re.MULTILINE)

    return {
        "status": status,
        "conflicts": grab_int("conflicts"),
        "decisions": grab_int("decisions"),
        "propagations": grab_int("propagations"),
        "restarts": grab_int("restarts"),
        "learned_clauses": grab_int("learned"),
        "reduced": grab_int("reduced"),
        "subsumed": grab_int("subsumed"),
        "strengthened": grab_int("strengthened"),
        "vivified": grab_int("vivified"),
        "process_time_reported": grab_float(
            r"^c total process time since initialization:\s*([0-9.]+)"
        ),
        "real_time_reported": grab_float(
            r"^c total real time since initialization:\s*([0-9.]+)"
        ),
        "memory_reported_mb": grab_float(
            r"^c maximum resident set size of process:\s*([0-9.]+)"
        ),
        "exit_code_reported": int(m_exit.group(1)) if m_exit else None,
    }

def parse_glucose(output):

    def grab_int(pattern):
        m = re.search(pattern, output, re.MULTILINE)
        return int(m.group(1).replace(",", "")) if m else None

    def grab_float(pattern):
        m = re.search(pattern, output, re.MULTILINE)
        return float(m.group(1).replace(",", "")) if m else None

    if re.search(r"^s UNSATISFIABLE", output, re.MULTILINE):
        status = "UNSAT"
    elif re.search(r"^s SATISFIABLE", output, re.MULTILINE):
        status = "SAT"
    elif re.search(r"^s INDETERMINATE", output, re.MULTILINE):
        status = "INDETERMINATE"
    else:
        status = "UNKNOWN"

    return {
        "status": status,

        "variables": grab_int(
            r"^c \|\s+Number of variables:\s+([0-9,]+)"
        ),

        "clauses": grab_int(
            r"^c \|\s+Number of clauses:\s+([0-9,]+)"
        ),

        "restarts": grab_int(
            r"^c restarts\s+:\s+([0-9,]+)"
        ),

        "blocked_restarts": grab_int(
            r"^c blocked restarts\s+:\s+([0-9,]+)"
        ),

        "reduce_db_calls": grab_int(
            r"^c nb ReduceDB\s+:\s+([0-9,]+)"
        ),

        "removed_clauses": grab_int(
            r"^c nb removed Clauses\s+:\s+([0-9,]+)"
        ),

        "avg_learnt_size": grab_float(
            r"^c average learnt size\s+:\s+([0-9.]+)"
        ),

        "learnts_dl2": grab_int(
            r"^c nb learnts DL2\s+:\s+([0-9,]+)"
        ),

        "learnts_size2": grab_int(
            r"^c nb learnts size 2\s+:\s+([0-9,]+)"
        ),

        "learnts_size1": grab_int(
            r"^c nb learnts size 1\s+:\s+([0-9,]+)"
        ),

        "conflicts": grab_int(
            r"^c conflicts\s+:\s+([0-9,]+)"
        ),

        "decisions": grab_int(
            r"^c decisions\s+:\s+([0-9,]+)"
        ),

        "propagations": grab_int(
            r"^c propagations\s+:\s+([0-9,]+)"
        ),

        "reduced_clauses": grab_int(
            r"^c nb reduced Clauses\s+:\s+([0-9,]+)"
        ),

        "cpu_time_reported": grab_float(
            r"^c CPU time\s+:\s+([0-9.]+)"
        ),
    }

def parse_maplesat(output):
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
        "actual_reward": grab_float(r"^actual reward\s+:\s+([0-9.]+)"),
        "cpu_time_reported": grab_float(r"^CPU time\s+:\s+([0-9.]+)"),
    }

def parse_by_solver(name, output):
    name_lower = name.lower()

    if "cadical" in name_lower:
        return parse_cadical(output)

    if "glucose" in name_lower:
        return parse_glucose(output)

    if "maple" in name_lower:
        return parse_maplesat(output)

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

        row = {
            "solver": name,
            "instance": cnf_path.name,
            "path": str(cnf_path),
            "status": parsed.get("status", detect_status(output)),
            "runtime_sec": elapsed,
            "returncode": proc.returncode,
            "timeout": False,
        }

        row.update(empty_stats_row())
        row.update(parsed)

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
        }

        row.update(empty_stats_row())
        row.update(parsed)
        row["status"] = "TIMEOUT"

        return row

def run_pysat_minisat(cnf_path):
    start = time.time()
    try:
        cnf = CNF(from_file=str(cnf_path))
        with Minisat22(bootstrap_with=cnf.clauses) as solver:
            sat = solver.solve_limited(expect_interrupt=True)
            elapsed = time.time() - start
            stats = solver.accum_stats()

        if sat is True:
            status = "SAT"
        elif sat is False:
            status = "UNSAT"
        else:
            status = "UNKNOWN"

        return {
            "solver": "pysat_minisat22",
            "instance": cnf_path.name,
            "path": str(cnf_path),
            "status": status,
            "runtime_sec": elapsed,
            "returncode": 0,
            "timeout": False,
            "conflicts": stats.get("conflicts"),
            "decisions": stats.get("decisions"),
            "propagations": stats.get("propagations"),
            "restarts": stats.get("restarts"),
        }


    except Exception as e:
        return {
            "solver": "pysat_minisat22",
            "instance": cnf_path.name,
            "path": str(cnf_path),
            "status": f"ERROR: {e}",
            "runtime_sec": None,
            "returncode": None,
            "timeout": False,
            "conflicts": None,
            "decisions": None,
            "propagations": None,
            "restarts": None,
        }


def main():
    with open("solvers.json") as f:
        solvers = json.load(f)

    cnfs = sorted(BENCHMARK_DIR.rglob("*.cnf"))

    if N_INSTANCES is not None:
        cnfs = cnfs[:N_INSTANCES]

    if not cnfs:
        raise FileNotFoundError(f"No .cnf files found under {BENCHMARK_DIR}")

    rows = []

    total_runs = len(cnfs) * len(solvers)
    run_id = 0

    for cnf in cnfs:
        print(f"\nInstance: {cnf}")

        for name, exe in solvers.items():
            run_id += 1
            print(f"  [{run_id}/{total_runs}] Running {name}...")

            row = run_external_solver(name, exe, cnf)
            rows.append(row)

            print(
                f"    status={row['status']}, "
                f"time={row['runtime_sec']:.2f}s, "
                f"conflicts={row.get('conflicts')}"
            )

            pd.DataFrame(rows).to_csv("smoke_test_results.csv", index=False)

    df = pd.DataFrame(rows)
    print(df)

    df.to_csv("smoke_test_results.csv", index=False)
    print("\nSaved smoke_test_results.csv")

if __name__ == "__main__":
    main()
