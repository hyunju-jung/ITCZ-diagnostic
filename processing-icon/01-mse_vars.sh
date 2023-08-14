#!/bin/bash -l
#SBATCH --job-name=ke  # Specify job name
#SBATCH --partition=cip    # Specify partition name
#SBATCH --nodes=1              # Specify number of nodes
#SBATCH --ntasks=8
#SBATCH --time=02:00:00        # Set a limit on the total run time
#SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --mail-user=hyunju.jung@kit.edu # Set your e-mail
#SBATCH --output=ke-remap.out    # File name for standard output
#SBATCH --error=ke-remap.err     # File name for standard error output
#SBATCH --mem=100G
#SBATCH --array=0-960     

module purge
module load python/3.9-2021.11
module load enstools/2020.11.a2-py3
module load spack
module load icon-tools
module load hdf5-blosc

module list

INDICATOR="explicit" #"high_resolution/param"
files=(`ls /archive/meteo/w2w-p2/B6/natureruns_new/${INDICATOR}/obs_DOM01_ML_*.nc | sort`)
#files=(`ls /archive/meteo/w2w-p2/B6/${INDICATOR}/output/obs_DOM01_ML_*.nc | sort`)
DEST="data/${INDICATOR}"
PREFIX="ke_var_"

#--------remapping
num=$(( ${SLURM_ARRAY_TASK_ID}+1 )) #73 #121
i=$(printf "%04d\n" ${num})
echo "i = $i"

#grid files for 13- and 5-km runs
#grid_file="/archive/meteo/w2w-p2/B6/high_resolution/grid/grid_DOM01.nc"
grid_file="/archive/meteo/w2w-p2/B6/DA/13km/grid_DOM01.nc"

cat > remap_bc_${i}.namelist << EOF
&remap_nml
    in_grid_filename               = "${grid_file}"
    in_filename                    = "${files[$SLURM_ARRAY_TASK_ID]}"
    in_type                        = 2
    out_filename                   = "${DEST}/ke_var_reg_${i}.nc"
    out_type                       = 1
    lsynthetic_grid                = .TRUE.
    corner1                        = -180.,-30.
    corner2                        = 180., 30.
    nxpoints                       = 1801 
    nypoints                       = 301
/


EOF

cat > input_bc_${i}.namelist << EOF
&input_field_nml
    inputname                      = "temp"
    outputname                     = "temp" 
/
&input_field_nml
    inputname                      = "qv"
    outputname                     = "qv" 
/
&input_field_nml
    inputname                      = "qi"
    outputname                     = "qi" 
/
&input_field_nml
    inputname                      = "pres"
    outputname                     = "pres" 
/
EOF


echo 'remapping'
iconremap --remap_nml remap_bc_${i}.namelist --input_field_nml input_bc_${i}.namelist
echo 'remap is done'
rm remap_bc_${i}.namelist 
rm input_bc_${i}.namelist
#rm data/E5/ke_var_${i}.nc

#--------remapping
python -W ignore scripts/conceptual_vars_bug_fixed.py --source $DEST/ke_var_reg_${i}.nc --dest $DEST --prefix $PREFIX

#rm data/E5/ke_var_reg_${i}.nc
