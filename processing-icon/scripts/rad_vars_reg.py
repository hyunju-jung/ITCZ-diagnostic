import numpy as np
import xarray as xr
import argparse
import glob
import sys
sys.path.append("/project/meteo/w2w/B6/Hyunju/scripts")
from constant import *

'''
ICON: atm_phy_schemes/mo_radiation.f90
ddt_temp_radlw = -1 * lwflxall * cf
cf = 1/(rho*z*(pcd+(pcv-pcd)*qv))

cf: the conversion factor for flux divergence to heating rate
pcd: specific heat at constant volume for dry air
pcv: specific heat at constant volume for water vapor.
'''

def get_inverse_cf(rho, qv):
    '''
    Calculate 1/cf
    
    Parameters
    ----------
    rho: xarray.DataArray or np.ndarray
            array of density
    
    qv: xarray.DataArray or np.ndarray
            array of specific humidity
    
    Returns
    -------
    icf: xarray.DataArray or np.ndarray
    
    '''
    pcd=cvd
    pcv=cvv
    #print(rho.shape, qv.values.shape, z_full.shape)
    #icf=rho*z_full*(pcd+(pcv-pcd)*qv)
    icf=rho*(pcd+(pcv-pcd)*qv)
    
    return icf

def find_temp_tendency(ds, odir):
    '''
    find vars for temperature tendency due to radiation
    
    Parameters
    ----------
    ds: xarray.Dataset
    
    odir: string
            directory for simulation
    
    Returns
    -------
    ds: xarray.Dataset
            new dataset including vars of temperature tendency 
    
    '''
    ddt_rad = ['ddt_temp_radlw', 'ddt_temp_radsw'] 
    find_ddt_rad = True
    
    #find if ddt_rad is in the same dataset
    for onetime_var in ds.data_vars:
        for valid_name in ddt_rad:
            if valid_name in onetime_var.lower():
                find_ddt_rad = False
                print("var: %s " % onetime_var)
                break

    if find_ddt_rad:
        ds_add = xr.open_dataset("%s/nature_run_DOM01_ML_timeavg.nc" % odir)
        ds_add = ds_add.where(ds_add.lon < 180., drop=True)
        
        #add ddt_rad variables
        for onetime_var in ddt_rad:
            ds[onetime_var] = xr.DataArray(ds_add[onetime_var].values, dims = ['time', 'height', 'lat', 'lon'],
                                          coords=[ds.time, ds.height, ds.lat, ds.lon])
    
    return ds

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--odir", required=True, help="input files")
    parser.add_argument("--prefix", required=True, help="prefix for output file")
    
    args=parser.parse_args()
        
    ofiles=glob.glob("%s/obs_DOM01_ML_reg_*_timeavg.nc" % args.odir)
        
    ds=xr.open_mfdataset(ofiles)

    rho = R*ds.temp/ds.pres
    
    icf=get_inverse_cf(rho, ds.qv) 
    #icf_reg = ifunc(icf)
    
    ds = find_temp_tendency(ds, args.odir)
    print(ds)
    lwflx=ds.ddt_temp_radlw*icf.values
    swflx=ds.ddt_temp_radsw*icf.values
    
    new_ds=xr.Dataset()
    new_ds['lwrad']=lwflx
    new_ds['swrad']=swflx
    #new_ds=new_ds.rename({'height_3':'height'})

    new_ds=new_ds.where(new_ds.height > 50., drop=True)
    new_ds['lat']=np.round(new_ds.lat,2)
    new_ds['lon']=np.round(new_ds.lon,2)
    
    dest=args.prefix+'timeavg.nc'
    #new_ds.to_netcdf(dest)
    