#!/bin/bash
#SLURM SUBMISSION SCRIPT
#SBATCH -J MGnify                     # job name
#SBATCH -N 1                               # number of nodes
#SBATCH -c 2
#SBATCH -o %j.out                            # stdout file name (%j: job ID)
#SBATCH -e %j.err                             # stderr file name (%j: job ID)
#SBATCH -t 6-23:00:00                        # max run time (hh:mm:ss), max 72h!
#SBATCH --mem=16G

## load modules
module purge
module load use.own
module load conda
source activate PATH_TO_CONDA_ENV

python ./download_assemblies.py -i ./analyses_and_assembly.txt -d 1
