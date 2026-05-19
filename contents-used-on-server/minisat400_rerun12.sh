#!/bin/bash
#SBATCH --job-name=sat400
#SBATCH --account=bgvu-delta-cpu
#SBATCH --partition=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=00:06:00
#SBATCH --output=logs_minisat/%A_%a.out
#SBATCH --error=logs_minisat/%A_%a.err

export LD_LIBRARY_PATH=$HOME/minisat-install/lib:$LD_LIBRARY_PATH

module load cray-python/3.11.7
source ~/venvs/satsolvers/bin/activate

cd /projects/bgvu/ttraw/final-project

python minisat_solver_cluster.py
