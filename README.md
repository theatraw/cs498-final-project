The pipeline is as follows:

Grab the SAT Competition 2023 Main Track Benchmarks from here: 
https://zenodo.org/records/11426992?preview_file=sat-competition-2023-main-benchmarks.zip
Unzip the data into a folder called "benchmarks" and decompress all 400 instances.

Clone the following repos and run "make" for all of them:
https://github.com/audemard/glucose
https://github.com/arminbiere/cadical
https://github.com/curtisbright/maplesat
https://github.com/niklasso/minisat

I used bulk_parallel_cluster.py to run the three solvers on the 400 instances. sat400.sh was the script to submit to the cluster.
(I ran this on the NCSA Delta cluster.) After the jobs all finished, I used merge_jobs.py to create the complete CSV dataset of results.

I separately ran the baseline, which used minisat_solver_cluster.py and minisat400_baseline.sh.

These files are in contents-used-on-server/.

Then I ran my analysis locally to explore my dataset. The figures I used in my final report came from:  make_cactus.py, 
category_cactus.py, sat_vs_unsat_cactus.py, make_final_metric_plots_updated.py, and par2_calc.py.

This repo is pretty messy, but these are the main pieces to it.

