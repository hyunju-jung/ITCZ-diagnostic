#!/bin/bash -l
# Download or copy requried input files
##SBATCH --ntasks-per-node=1
##SBATCH --nodes=16
#SBATCH --ntasks=8
#SBATCH --partition=cip
#SBATCH --mem=100G
#SBATCH --time=1:00:00
#SBATCH --output=remap.out 
#SBATCH --error=remap.err
#SBATCH --export=NONE
##SBATCH --mail-type=ALL
#SBATCH --mail-user=hyunju.jung@kit.edu
#SBATCH --job-name=remap
#SBATCH --array=120-1080 #72-1032 #0-960  #721 #169 

module purge
module load spack cdo
module load hdf5-blosc
module load icon-tools #/2.1.0-gcc-9
module list

num=$(( ${SLURM_ARRAY_TASK_ID}+1 ))
i=$(printf "%04d\n" ${num})

#---grid information
#grid_file="/archive/meteo/w2w-p2/B6/DA/13km/grid_DOM01.nc"
grid_file="/archive/meteo/w2w-p2/B6/high_resolution/grid/grid_DOM01.nc"

#---sel cases
#odirs=( "param" "shallow" "stochastic_shallow" "explicit" )
odirs=( "output" )
od_data="E5"

for od in ${odirs[@]}
do

#---file names
#in_filename="/archive/meteo/w2w-p2/B6/natureruns_new/${od}/obs_DOM01_ML_${i}.nc"
#out_filename="data/${od}/obs_DOM01_reg_ML_${i}.nc"

in_filename="/archive/meteo/w2w-p2/B6/high_resolution/${od}/obs_DOM01_ML_${i}.nc"
out_filename="data/${od_data}/obs_DOM01_level90_ML_${i}.nc"
final_filename="data/${od_data}/obs_DOM01_reg_level90_${i}.nc"

if [ -f ${final_filename} ]; then
   echo ${final_filename}
   echo "file already exists"
  
else
 echo 'creating file'

#select the near-surface level
cdo --no_history -sellevel,90,90 -selvar,pres,temp,qv ${in_filename} ${out_filename}

#remapping
cat > remap_bc_${i}.namelist << EOF
&remap_nml
    in_grid_filename               = "${grid_file}"
    in_filename                    = "${out_filename}"  
    in_type                        = 2
    out_filename                   = "${final_filename}"    
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
    inputname                      = "pres"
    outputname                     = "pres" 
/
&input_field_nml
    inputname                      = "temp"
    outputname                     = "temp" 
/
&input_field_nml
    inputname                      = "qv"
    outputname                     = "qv" 
/
EOF

echo 'remapping'
iconremap --remap_nml remap_bc_${i}.namelist --input_field_nml input_bc_${i}.namelist
echo 'remap is done'
rm remap_bc_${i}.namelist 
rm input_bc_${i}.namelist
fi

rm ${out_filename}

done
