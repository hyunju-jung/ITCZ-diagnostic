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
#SBATCH --array=72-72 #72-1032 #0-960  #721 #169 

echo ${SLURM_ARRAY_TASK_ID}
num=$(( ${SLURM_ARRAY_TASK_ID}+1 ))
i=$(printf "%04d\n" ${num})
echo "i = $i"

oi=$(printf "%03d\n" ${SLURM_ARRAY_TASK_ID})

grid_file="/archive/meteo/w2w-p2/B6/DA/13km/grid_DOM01.nc"
#grid_file="/archive/meteo/w2w-p2/B6/high_resolution/grid/grid_DOM01.nc"

#out_filename                   = "data/${odir}/obs_reg_DOM01_ML_${i}.nc"
#in_filename                    = "/archive/meteo/w2w-p2/B6/high_resolution/param/obs_DOM01_ML_${i}.nc"

odirs=( "param" "shallow" "stochastic_shallow" "explicit" )
#odirs=( "param" )
#od_data="P5"

for od in ${odirs[@]}
do
in_filename="/archive/meteo/w2w-p2/B6/natureruns_new/${od}/obs_DOM01_ML_${i}.nc"
out_filename="data/${od}/obs_DOM01_reg_ML_${i}.nc"

#in_filename="/archive/meteo/w2w-p2/B6/high_resolution/${od}/obs_DOM01_ML_${i}.nc"
#out_filename="data/${od_data}/obs_DOM01_reg_ML_${i}.nc"

#echo " file is rain_reg_DOM01_ML_0${i}.nc"
if [ -f ${out_filename} ]; then
   echo "file already exists"
  
else
 echo 'creating file'

cat > remap_bc_${i}.namelist << EOF
&remap_nml
    in_grid_filename               = "${grid_file}"
    in_filename                    = "${in_filename}"  
    in_type                        = 2
    out_filename                   = "${out_filename}"    
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

module purge
module load spack cdo
module load hdf5-blosc
module load icon-tools #/2.1.0-gcc-9
module list

echo 'remapping'
iconremap --remap_nml remap_bc_${i}.namelist --input_field_nml input_bc_${i}.namelist
echo 'remap is done'
rm remap_bc_${i}.namelist 
rm input_bc_${i}.namelist
fi

#select the near-surface level
final_filename="data/${od}/obs_DOM01_reg_level90_${i}.nc"
#final_filename="data/${od_data}/obs_DOM01_reg_level90_${i}.nc"
cdo --no_history -sellevel,90,90 -selvar,pres,temp,qv ${out_filename} ${final_filename}

rm ${out_filename}

done
