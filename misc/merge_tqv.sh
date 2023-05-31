#!/bin/bash -l

module load spack cdo
module load hdf5-blosc

opath="/archive/meteo/w2w-p2/B6/high_resolution/"

#spinup files
#for FILENAME in $(ls -lX ${opath}output_spinnup/nature_run_DOM01_ML_00??.nc | head -72)
#do
#    echo ${FILENAME}
#    num=${FILENAME:(-27)}
#    cdo selvar,tqv ${FILENAME} data/${num}    
#done

#some have different remapped grid in the spinup files
#for FILENAME in $(ls -lX data/nature_run_DOM01_ML_00??.nc | head -49)
#do
#    echo ${FILENAME}
#    num=${FILENAME:(-27)}
#    cdo -P 8 remapcon,grid_des.txt ${FILENAME} data/remap_${num}    
#done

#change remap filename
for FILENAME in $(ls -lX data/remap_nature_run_DOM01_ML_00??.nc)
do
    num=${FILENAME:(-27)}
    mv ${FILENAME} data/${num}
    echo "data/"${num}
    
done

#analysis period
#for FILENAME in $(ls -lX ${opath}param/nature_run_DOM01_ML_????.nc | tail -962)
#do
#    num=${FILENAME:(-27)}
#    cdo selvar,tqv ${FILENAME} data/${num}    
#done

#cdo --no_history mergetime data/nature_run_DOM01_ML_????.nc data/tqv-5km-param.nc