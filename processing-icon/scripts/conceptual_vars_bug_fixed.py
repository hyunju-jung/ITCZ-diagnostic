import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import pickle
from enstools.misc import swapaxis
from enstools.io import read, write
import sys
sys.path.append('/project/meteo/w2w/B6/Hyunju/scripts')
from constant import g0
from atm_var import func_geopot
from horizontal_interpolation import get_interpolator

cp = 1004. #J kg-1 K-1
Lv = 2.501e6 #J kg-1
Lf = 333.7e3 #J kg-1

def get_vertical_dim(da, vertical_dim=None):
    """"
    To get variable name for vertical coordinate
    
    Parameters
    ----------
    da: xarray.Dataset or xarray.DataArray
            array with vertical coordinate 
    
    Returns
    -------
    vertical_dim: string
            variable name for vertical coordinate
    """"
    if isinstance(da, xr.DataArray):
        vertical_dim_names = ["pres", "p", "lev", "level", "isobaric", "layer", "hybrid", "height", "height_2","height_3"]
        for dimi, dim in enumerate(da.dims):
            for valid_name in vertical_dim_names:
                if valid_name in dim.lower():
                    vertical_dim = dimi
                    break
            if vertical_dim is not None:
                break
    return vertical_dim

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, nargs="+", help="input files")
    parser.add_argument("--dest", required=True, help="folder for output")
    parser.add_argument("--prefix", required=True, help="prefix for output file")
    
    args=parser.parse_args()
    ds=read(args.source)
    ds = ds.isel(time = slice(0,1))
    
    #reorder required
    #find a name of vertical coordinate and reorder it
    vertical_dim = get_vertical_dim(ds.temp)
    temp = swapaxis(ds.temp, vertical_dim, 0)
    qv = swapaxis(ds.qv, vertical_dim, 0)
    qi = swapaxis(ds.qi, vertical_dim, 0)
    
    for key in ds.data_vars.keys():
        if key == "z_ifc":
            z_ifc=ds.z_ifc.mean('ncells')
    try:
        z_ifc
    except NameError:
        z_ifc=xr.open_dataset('/project/meteo/w2w/B6/Hyunju/z_ifc.nc')['z_ifc'] 
    
    geopot = 0.5*(z_ifc[1:].values + z_ifc[:-1].values)*g0
    dim_num = len(ds.temp.shape)
    
    for i in range(dim_num-1):
        geopot=geopot[...,np.newaxis]
    
    #Dry static energy: s = geopotential + cp*temp
    #Moist static energy: h = s + Lv*qv - Lf*qi
    s = geopot + cp*temp
    h = s + Lv*qv - Lf*qi
    
    #reorder dimensions as in the source data
    s = swapaxis(s, vertical_dim, 0)
    h = swapaxis(h, vertical_dim, 0)
    
    new_ds = xr.Dataset()
    new_ds['h'] = h
    new_ds['s'] = s
    new_ds = new_ds.where(new_ds.height >= 25., drop=True)
    #new_ds['lat'] = np.round(new_ds.lat, 2)
    
    ofilename=args.dest+'/'+args.prefix+args.source[0][-7:]
    new_ds.to_netcdf(ofilename)
    print('completed!')
