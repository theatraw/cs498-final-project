#!/bin/bash
#SBATCH --job-name=sat-test
#SBATCH --account=bgvu-delta-cpu
#SBATCH --partition=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:02:00
#SBATCH --array=0-29%10
#SBATCH --output=logs/%A_%a.out
#SBATCH --error=logs/%A_%a.err

mkdir -p logs results

module load cray-python/3.11.7
source ~/venvs/satsolvers/bin/activate

cd /projects/bgvu/ttraw/final-project
python bulk_parallel_cluster.py

