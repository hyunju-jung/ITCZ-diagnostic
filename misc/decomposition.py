import xarray as xr
import numpy as np
import argparse
import sys
sys.path.append('../../scripts/')
from constant import cp, Lv

rho=1.2
#flists=['param', 'shallow', 'stochastic_shallow', 'explicit', 'P5', 'E5']

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="calculating avg and flux contributions")
    parser.add_argument("--odir", required=True, help="odir")
    args=parser.parse_args()
    
    od = args.odir
    
    ds = xr.open_dataset('data/%s/flx_vars_mergetime.nc' % od)
    
    ds['ce']=-ds['ce']
    ds['ch']=-ds['ch']
    ds['dqv']=-ds['dqv']
    ds['dtemp']=-ds['dtemp']
    
    u_lh = ds.ce * ds.usfc
    u_sh = ds.ch * ds.usfc

    u_lh_mean = u_lh.mean(['lon', 'time'])
    dqv_mean = ds.dqv.mean(['lon','time'])

    u_sh_mean = u_sh.mean(['lon', 'time'])
    dtemp_mean = ds.dtemp.mean(['lon','time'])

    term1_lh = Lv * rho * u_lh_mean * dqv_mean
    term1_sh = cp * rho * u_sh_mean * dtemp_mean 


    #{u}*
    u_lon_mean = u_lh.mean('lon')
    u_lon_mean_str = u_lon_mean - u_lon_mean.mean('time')

    #{dqv}*
    dqv_lon_mean = ds.dqv.mean('lon')
    dqv_lon_mean_str = dqv_lon_mean - dqv_lon_mean.mean('time')

    term2_lh = u_lon_mean_str * dqv_lon_mean_str
    term2_lh = Lv * rho * term2_lh.mean('time')

    #{u}*
    u_sh_lon_mean = u_sh.mean('lon')
    u_sh_lon_mean_str = u_sh_lon_mean - u_sh_lon_mean.mean('time')

    #{dtemp}*
    dtemp_lon_mean = ds.dtemp.mean('lon')
    dtemp_lon_mean_str = dtemp_lon_mean - dtemp_lon_mean.mean('time')

    term2_sh = u_sh_lon_mean_str * dtemp_lon_mean_str
    term2_sh = cp * rho * term2_sh.mean('time')


    u_lh_p = u_lh - u_lh.mean('lon')
    dqv_p = ds.dqv - ds.dqv.mean('lon')
    u_sh_p = u_sh - u_sh.mean('lon')
    dtemp_p = ds.dtemp - ds.dtemp.mean('lon')

    term3_lh = u_lh_p*dqv_p
    term3_sh = u_sh_p*dtemp_p

    term3_lh = Lv * rho * term3_lh.mean(['lon', 'time'])
    term3_sh = cp * rho * term3_sh.mean(['lon', 'time'])
    
    term1 = term1_lh + term1_sh
    term2 = term2_lh + term2_sh
    term3 = term3_lh + term3_sh
    
    new_ds = xr.Dataset()
    new_ds['term1'] = xr.DataArray(term1.values, coords=[term1.lat], dims=['lat'])
    new_ds['term2'] = xr.DataArray(term2.values, coords=[term1.lat], dims=['lat'])
    new_ds['term3'] = xr.DataArray(term3.values, coords=[term1.lat], dims=['lat'])
    
    new_ds.to_netcdf('data/%s/decompose_timeavg.nc' % od)