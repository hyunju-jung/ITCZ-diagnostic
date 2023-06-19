#!/bin/bash -l
# Download or copy requried input files
#SBATCH --ntasks=8
#SBATCH --partition=cip
#SBATCH --mem=100G
#SBATCH --time=1:00:00
#SBATCH --output=flx_var.out 
#SBATCH --error=flx_var.err
#SBATCH --export=NONE
#SBATCH --mail-user=hyunju.jung@kit.edu
#SBATCH --job-name=sef_vars
##SBATCH --array=0-960

module purge
module load python/3.9-2021.11

#num=$(( ${SLURM_ARRAY_TASK_ID}+120 )) #72
#i=$(printf "%04d\n" ${num})
#echo "i = $i"

#----13km----
#DEST="param"
#nt_source="/archive/meteo/w2w-p2/B6/natureruns_new/${DEST}/nature_run_DOM01_ML_${i}.nc"
#sfc_source="data/${DEST}/obs_DOM01_reg_level90_${i}.nc"

for num in {150..1080}
do
  i=$(printf "%04d\n" ${num})
  echo "i = $i"

  flx_file="data/${DEST}/flx_vars_${i}.nc"

if [ -f ${flx_file} ]; then
  echo "file already exists: ${flx_file}"
else

DEST="E5"
nt_source="/archive/meteo/w2w-p2/B6/high_resolution/output/nature_run_DOM01_ML_${i}.nc"
sfc_source="data/${DEST}/obs_DOM01_reg_level90_${i}.nc"

python -W ignore SEF_variables.py --sfc_source ${sfc_source} --nt_source ${nt_source} --dest ${DEST}

fi
done


