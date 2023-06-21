#!/bin/bash -l
# Download or copy requried input files
#SBATCH --ntasks=8
#SBATCH --partition=cip
#SBATCH --mem=100G
#SBATCH --time=7:00:00
#SBATCH --output=SEF_analysis.out 
#SBATCH --error=SEF_analysis.err
#SBATCH --export=NONE
#SBATCH --mail-user=hyunju.jung@kit.edu
#SBATCH --job-name=SEF_analysis

module purge
module load python/3.9-2021.11

#odirs=( "shallow" "stochastic_shallow" "explicit" ) #"P5" "E5")
odirs=( "E5" )

for od in ${odirs[@]}
do

echo "run python script in ${od}"
#python -W ignore decomposition.py --odir ${od}
python -W ignore DeMott_diagnostics.py --dest ${od}

done
