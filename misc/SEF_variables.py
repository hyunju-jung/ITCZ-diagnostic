import xarray as xr
from enstools.io import read
import numpy as np
import pandas as pd
import glob
import argparse
import pickle
import sys
sys.path.append('/project/meteo/w2w/B6/Hyunju/icon_wrapping/')
from icon_nwp_turbtrans_hydro import sr_dqv_2d, ape_sst_qobs_1d 
sys.path.append('/project/meteo/w2w/B6/Hyunju/scripts')
from constant import *

z_ifc=xr.open_dataset('../../z_ifc.nc')['z_ifc']
z_full=0.5*(z_ifc[1:].values + z_ifc[:-1])
z_full=z_full.rename({'height_2':'height'})

def find_2files(fname):
    f_num = find_int(fname)
    f_int = int(f_num)
    f_next = f_int + 1

    new_name = fname.replace(f_num, '%04d' % f_next)
    
    flists = [fname, new_name]
    return flists

def find_int(fname):
    f_int = fname.split('/')[-1]
    f_int = f_int.split('_')[-1]
    f_int = f_int.split('.')[0]

    return f_int

def cal_fluxes(odir, da):
    
    #Different inital time for the runs
    #to convert accumulated vars to averaged ones
    if odir == 'P5':
        itime = np.datetime64('2020-11-10T00')
        
    elif odir == 'E5':
        itime = np.datetime64('2020-11-10T00')
        
    else:
        itime=np.datetime64('2020-07-31T00')
    
    time = da.time.values - itime  
    
    time = time*1e-9
    time = time.astype(float)
    time = time[:,np.newaxis, np.newaxis]
    
    flx = - time*da
    flx = flx.diff('time') / np.diff(time, axis = 0)
    
    return flx

def drop_timestep(ds):
    for one_time in ds.time.values:
        dt=pd.to_datetime(one_time)
        
        if int(dt.strftime('%M')) != 0:
            ds = ds.drop_sel(time = one_time)
            
    return ds

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="averaged var to instantaneous")
    parser.add_argument("--sfc_source", required=True, help="input variables")
    parser.add_argument("--nt_source", required=True, help="input variables")
    parser.add_argument("--dest", help="folder for output")
    args=parser.parse_args()

    #ofiles = [args.sfc_source, find_file(args.sfc_source)]
    num = find_int(args.sfc_source)
    
    print("------%s-----" % num)
    
    ds1 = read( find_2files(args.sfc_source) )
    ds2 = read( find_2files(args.nt_source) )
    ds2 = drop_timestep(ds2) # two time steps -> one time step in E5
    ds2 = ds2.where(ds2.lon < 180., drop=True)
    print(ds2.time.values)
    
    #average as surface fluxes are averaged values
    temp=0.5*(ds1.temp[0,0,:,:].values + ds1.temp[1,0,:,:])
    pres=0.5*(ds1.pres[0,0,:,:].values + ds1.pres[1,0,:,:])
    qv=0.5*(ds1.qv[0,0,:,:].values + ds1.qv[1,0,:,:])
    
    u=0.5*(ds2.u_10m[0,0,:,:].values + ds2.u_10m[1,0,:,:])
    v=0.5*(ds2.v_10m[0,0,:,:].values + ds2.v_10m[1,0,:,:])
    
    lh=cal_fluxes(args.dest, ds2.alhfl_s)
    sh=cal_fluxes(args.dest, ds2.ashfl_s)

    nlat=ds1.dims['lat']
    nlon=ds1.dims['lon']
    dz=z_full[-1]
    
    #-----compute moist and temperature difference
    #SST and dtemp
    sst=ape_sst_qobs_1d(np.radians(ds1.lat), ds1.lat.shape[0])
    dtemp=temp - sst[:,np.newaxis] #to make the shape identical
    
    #dqv -> n_ncell: nlon | nt: nlat
    dqv=sr_dqv_2d(np.radians(ds1.lat), dz, qv, pres, temp, nlat, nlon)
    
    usfc=np.sqrt(u**2 + v**2)
    rho = pres / (R * temp)
    
    usfc=usfc.values[np.newaxis,:,:]
    rho=rho.values[np.newaxis,:,:]
    dqv=dqv[np.newaxis,:,:]
    dtemp=dtemp.values[np.newaxis,:,:]
    
    ce=lh/(Lv*usfc*dqv*rho)
    ch=sh/(cp*usfc*dtemp*rho)

    time_in = ds1.time[:1]
    new_ds = xr.Dataset()
    new_ds['ce'] = xr.DataArray(ce.values, coords=[time_in, ds1.lat, ds1.lon], dims=['time','lat','lon'])
    new_ds['ch'] = xr.DataArray(ch.values, coords=[time_in, ds1.lat, ds1.lon], dims=['time','lat','lon'])
    new_ds['usfc'] = xr.DataArray(usfc, coords=[time_in, ds1.lat, ds1.lon], dims=['time','lat','lon'])
    new_ds['rho'] = xr.DataArray(rho, coords=[time_in, ds1.lat, ds1.lon], dims=['time','lat','lon'])
    new_ds['dqv'] = xr.DataArray(dqv, coords=[time_in, ds1.lat, ds1.lon], dims=['time','lat','lon'])
    new_ds['dtemp'] = xr.DataArray(dtemp, coords=[time_in, ds1.lat, ds1.lon], dims=['time','lat','lon'])
    
    new_ds['lat'] = np.around(new_ds.lat, 2)
    new_ds['lon'] = np.around(new_ds.lon, 2)

    new_ds.to_netcdf('data/%s/flx_vars_%s.nc' % (args.dest, num))
    