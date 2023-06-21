import xarray as xr
from enstools.io import read
import numpy as np
import glob
import argparse
import pickle
from SEF_variables import cal_fluxes, drop_timestep

def flux_diagnostics(ds, xvar, yvar, xrange, yrange, flux='sef'):
    """
    Calculate 2D diagram as in Hsu et al., 2022
    
    Parameters
    ----------
    ds : xarray.dataset
    
    xvar : string
    
    yvar : string
    
    xrange : ndarray
    
    yrange : ndarray
    
    flux : string, optional
    
    Returns
    -------
    value_arr, freq_arr : list of ndarrays
    
    """
    
    #check if x/y range is correct
    if check_range(ds[xvar], xrange):
        raise ValueError("range of %s does not cover the whole spectrum." % xvar)
    if check_range(ds[yvar], yrange):
        raise ValueError("range of %s does not cover the whole spectrum." % yvar)
    
    nx=len(xrange)-1
    ny=len(yrange)-1
    
    value_arr = np.zeros((ny, nx))
    freq_arr = np.zeros((ny, nx))
    
    for i in range(nx):
        condition1 = ((ds[xvar] >= xrange[i]) & (ds[xvar] < xrange[i+1]))
        for j in range(ny):
            condition2 = ((ds[yvar] >= yrange[j]) & (ds[yvar] < yrange[j+1]))
            temp = ds[flux].where(condition1 & condition2, np.nan)
            
            value_arr[j,i] = np.nanmean(temp)
            freq = np.count_nonzero(~np.isnan(temp.values))
            
            if freq == 2: print("number counted 1: ", i, j)
            
            freq_arr[j,i] = freq
            
    return value_arr, freq_arr

def check_range(var, var_range):
    """
    Check if a range for distribution is appropriate
    
    Parameters
    ----------
    var : ndarray
    
    var_range : ndarray
    
    Returns
    -------
    
    boolean
    
    """
    if (np.min(var) >= var_range.min()) & (np.max(var) <= var_range.max()):
        return False
    else:
        return True
    
if __name__=="__main__":
    parser=argparse.ArgumentParser(description="averaged var to instantaneous")
    parser.add_argument("--dest", help="folder for output")
    args=parser.parse_args()
    
    #ofiles = glob.glob('/archive/meteo/w2w-p2/B6/natureruns_new/%s/nature_run_DOM01_ML_????.nc' % args.dest)
    ofiles = glob.glob('/archive/meteo/w2w-p2/B6/high_resolution/output/nature_run_DOM01_ML_????.nc')
    ofiles = sorted(ofiles)
    if args.dest == 'E5':
        ofiles = ofiles[-961:]
    print(len(ofiles))
    #alhfl_s = xr.open_mfdataset(ofiles)['alhfl_s']
    alhfl_s = read(ofiles)['alhfl_s']
    alhfl_s = drop_timestep(alhfl_s) # for E5
    alhfl_s = alhfl_s.where(alhfl_s.lon < 180., drop=True)
        
    lh = cal_fluxes(args.dest, alhfl_s)
    print(lh)
    ds = xr.open_dataset('data/%s/flx_vars_mergetime.nc' % args.dest)

    new_ds = xr.Dataset()
    new_coords = [ds.time, ds.lat, ds.lon]
    new_dims = ['time','lat','lon']
    new_ds['usfc'] = xr.DataArray(ds.usfc.values, coords=new_coords, dims=new_dims)
    new_ds['dqv'] = xr.DataArray(-1000.*ds.dqv.values, coords=new_coords, dims=new_dims)
    new_ds['lh'] = xr.DataArray(lh.values, coords=new_coords, dims=new_dims)
    
    latlim = 10 #25.
    new_ds = new_ds.sel(lat=slice(-latlim,latlim))
    
    xvar = 'usfc'
    yvar = 'dqv'
    
    min_lh = new_ds.lh.min(['time','lon']).values
    print(min_lh)
    pickle.dump(min_lh, open('min_lh_%s.pkl' % args.dest, 'wb'))
    
    print("xMinMax: ", new_ds[xvar].min().values, new_ds[xvar].max().values)
    print("yMinMax: ", new_ds[yvar].min().values, new_ds[yvar].max().values)
    
    xrange = np.linspace(0, 25, 26)
    yrange = np.linspace(0, 20, 21)
    
    var_arr, freq_arr = flux_diagnostics(new_ds, xvar, yvar, xrange, yrange, flux='lh')
    
    save_ds =xr.Dataset()
    x = 0.5*(xrange[1:]+xrange[:-1])
    y = 0.5*(yrange[1:]+yrange[:-1])
    save_coords = [y, x]
    save_dims = ['y', 'x']
    save_ds['var_arr'] = xr.DataArray(var_arr, coords=save_coords, dims=save_dims)
    save_ds['freq_arr'] = xr.DataArray(freq_arr, coords=save_coords, dims=save_dims)
    save_ds.attrs = {'lat band': 'between %.2fN/S' % latlim, 'xvar': xvar, 'yvar': yvar}
    save_ds.to_netcdf('data/%s/DeMott_%sNS.nc' % (args.dest, int(latlim)))
    #print(save_ds)