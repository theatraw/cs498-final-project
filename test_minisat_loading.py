import sys
import time
from pysat.formula import CNF
from pysat.solvers import Minisat22

cnf_path = sys.argv[1]

t0 = time.time()
cnf = CNF(from_file=cnf_path)
t1 = time.time()

with Minisat22(bootstrap_with=cnf.clauses) as solver:
    t2 = time.time()
    sat = solver.solve()
    t3 = time.time()
    stats = solver.accum_stats()

print("instance:", cnf_path)
print("status:", "SAT" if sat else "UNSAT")
print("load_time_sec:", t1 - t0)
print("solver_init_time_sec:", t2 - t1)
print("solve_time_sec:", t3 - t2)
print("total_time_sec:", t3 - t0)
print("num_vars:", cnf.nv)
print("num_clauses:", len(cnf.clauses))
print("stats:", stats)
