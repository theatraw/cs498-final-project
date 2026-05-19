#!/bin/bash
#SBATCH --job-name=minisat400
#SBATCH --account=bgvu-delta-cpu
#SBATCH --partition=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=00:06:00
#SBATCH --array=0-4%5
#SBATCH --output=logs_minisat/%A_%a.out
#SBATCH --error=logs_minisat/%A_%a.err

mkdir -p logs_minisat results_minisat

module load cray-python/3.11.7
source ~/venvs/satsolvers/bin/activate

cd /projects/bgvu/ttraw/final-project

python run_minisat_cluster.py
