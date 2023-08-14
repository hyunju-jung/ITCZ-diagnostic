import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import glob
import argparse
import time

hist_bin = np.arange(0,800,1)

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", required=True)

    args=parser.parse_args()
    
    ofiles=glob.glob("conceptual-model/data/%s/obs_DOM01_ML_reg_tot_prec_*.nc" % args.dir)
    ofiles=sorted(ofiles)
    print("%s : # %d" % (args.dir, len(ofiles)))
    ds=xr.open_mfdataset(ofiles)
    
    ds = ds.where( (ds.lat < 20.) & (ds.lat > -20.), drop=True)
    
    var = ds['tot_prec'].diff('time')
    
    print(var)
    hist, bin_edges=np.histogram(var, hist_bin, density=True)
    bins = 0.5*(bin_edges[1:] + bin_edges[:-1])
    new_ds=xr.Dataset()
    new_ds['hist'] = xr.DataArray(hist, coords=[bins], dims=['bins'])
    new_ds.attrs={'units':'mm/d', 'lat': 'between 20N/S', 'number of ofiles': '%d' % len(ofiles)}
    new_ds.to_netcdf('hist_daily_precip_reg_%s.nc' % args.dir)