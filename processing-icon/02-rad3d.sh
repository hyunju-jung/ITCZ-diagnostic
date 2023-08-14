#!/bin/bash -l
#SBATCH --job-name=rad  # Specify job name
#SBATCH --partition=cip    # Specify partition name
#SBATCH --nodes=1              # Specify number of nodes
#SBATCH --ntasks-per-node=1   # Specify number of tasks on each node
#SBATCH --time=02:00:00        # Set a limit on the total run time
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=hyunju.jung@kit.edu # Set your e-mail
#SBATCH --output=rad.out    # File name for standard output
#SBATCH --error=rad.err     # File name for standard error output
#SBATCH --mem=100G

module purge
module load python/3.9-2021.11
module load enstools/2020.11.a2-py3

dir="data/param"
PREFIX="${dir}/rad_"
python scripts/rad_vars_reg.py --odir $dir --prefix $PREFIX

dir="data/shallow"
PREFIX="${dir}/rad_"
python scripts/rad_vars_reg.py --odir $dir --prefix $PREFIX

dir="data/stochastic_shallow"
PREFIX="${dir}/rad_"
python scripts/rad_vars_reg.py --odir $dir --prefix $PREFIX

dir="data/explicit"
PREFIX="${dir}/rad_"
python scripts/rad_vars_reg.py --odir $dir --prefix $PREFIX

dir="data/P5"
PREFIX="${dir}/rad_"
python scripts/rad_vars_reg.py --odir $dir --prefix $PREFIX

dir="data/E5"
PREFIX="${dir}/rad_"
python scripts/rad_vars_reg.py --odir $dir --prefix $PREFIX

