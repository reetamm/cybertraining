#!/bin/bash
#SBATCH --job-name=mvnhmm-parallel
#SBATCH --output=parallel_viterbi.out
#SBATCH --error=parallel_viterbi.err
#SBATCH --partition=high_mem
#SBATCH --constraint=hpcf2018
#SBATCH --account=pi_gobbert
#SBATCH --qos=normal+
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1

module load Python/3.6.4-intel-2018a
mpirun python3 parallel_viterbi.py 

