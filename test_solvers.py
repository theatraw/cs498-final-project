import json
import subprocess

with open("solvers.json") as f:
    solvers = json.load(f)

cnf = "benchmarks/test.cnf"

for name, path in solvers.items():
    print(f"\n=== {name} ===")
    try:
        result = subprocess.run(
            [path, cnf],
            capture_output=True,
            text=True,
            timeout=30,
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print("return code:", result.returncode)
    except Exception as e:
        print("FAILED:", e)
