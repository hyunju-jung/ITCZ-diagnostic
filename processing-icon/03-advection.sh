#!/bin/bash -l
#SBATCH --job-name=adv  # Specify job name
#SBATCH --partition=cip    # Specify partition name
#SBATCH --nodes=1              # Specify number of nodes
#SBATCH --ntasks-per-node=1   # Specify number of tasks on each node
#SBATCH --time=01:00:00        # Set a limit on the total run time
#SBATCH --mail-type=FAIL       # Notify user by email in case of job #failure
#SBATCH --mail-user=hyunju.jung@kit.edu # Set your e-mail
#SBATCH --output=adv-%j.out    # File name for standard output
#SBATCH --error=adv-%j.err     # File name for standard error output
#SBATCH --mem=100G
##SBATCH --array=1-959

module purge
module load python/3.9-2021.11
#module load enstools/2020.11.a2-py3

odirs=( "param" "shallow" "stochastic_shallow" "explicit" )

for od in ${odirs[@]}
do

echo "doing ${od}"

#hfiles=(`ls data/${od}/ke_var_????.nc | sort `)
#vfiles=(`ls data/${od}/obs_DOM01_ML_reg_uv_????.nc | sort `)
#
#python -W ignore 99-yadvection.py --h ${hfiles[$SLURM_ARRAY_TASK_ID]} --v ${vfiles[$SLURM_ARRAY_TASK_ID]} --dir ${od}
python -W ignore 99-vertical-sum.py --dir ${od}

done

echo "high-res runs"

#INDICATOR="E5" #"high_res_param"
#hfiles=(`ls data/$INDICATOR/ke_var_????.nc | sort `)
#vfiles=(`ls data/$INDICATOR/obs_DOM01_ML_reg_uv_????.nc | sort `)
#
#python -W ignore 99-yadvection.py --h ${hfiles[$SLURM_ARRAY_TASK_ID]} --v ${vfiles[$SLURM_ARRAY_TASK_ID]} --dir $INDICATOR
#
#INDICATOR="P5" #"high_res_param"
#hfiles=(`ls data/$INDICATOR/ke_var_????.nc | sort `)
#vfiles=(`ls data/$INDICATOR/obs_DOM01_ML_reg_uv_????.nc | sort `)
#
#python -W ignore 99-yadvection.py --h ${hfiles[$SLURM_ARRAY_TASK_ID]} --v ${vfiles[$SLURM_ARRAY_TASK_ID]} --dir $INDICATOR

python -W ignore 99-vertical-sum.py --dir P5
python -W ignore 99-vertical-sum.py --dir E5