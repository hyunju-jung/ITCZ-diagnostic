#!/bin/bash -l

module load spack cdo
module load hdf5-blosc

opath="/archive/meteo/w2w-p2/B6/high_resolution/"

##-------tqv for P5----------
##some have different remapped grid in the spinup files
#for FILENAME in $(ls -lX ${opath}output_spinnup/nature_run_DOM01_ML_00??.nc | head -49)
#do
#    echo ${FILENAME}
#    num=${FILENAME:(-27)}
#    cdo selvar,tqv ${FILENAME} data/selvar_${num}
#    cdo -P 8 remapcon,grid_des.txt data/selvar_${num} data/${num}    
#done
#
#rm data/selvar_*.nc
#
##spinup files
#for FILENAME in $(ls -lX ${opath}output_spinnup/nature_run_DOM01_ML_{50..72}.nc)
#do
#    echo ${FILENAME}
#    num=${FILENAME:(-27)}
#    cdo selvar,tqv ${FILENAME} data/${num}    
#done
#
##analysis period
##for FILENAME in $(ls -lX ${opath}param/nature_run_DOM01_ML_????.nc | tail -962)
#for FILENAME in $(ls -lX ${opath}param/nature_run_DOM01_ML_00{73..99}.nc)
#do
#    num=${FILENAME:(-27)}
#    cdo selvar,tqv ${FILENAME} data/${num}    
#done
#
#cdo --no_history mergetime data/nature_run_DOM01_ML_????.nc data/tqv-5km-param.nc

#-------tqv for P5----------
for FILENAME in $(ls -lX ${opath}output/nature_run_DOM01_ML_*.nc)
do
    num=${FILENAME:(-27)}
    cdo -seltimestep,1/1 -selvar,tqv ${FILENAME} data/${num}    
done

cdo --no_history mergetime data/nature_run_DOM01_ML_????.nc data/tqv-5km-explicit.nc