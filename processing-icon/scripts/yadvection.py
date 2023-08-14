import xarray as xr
import glob
import numpy as np
import argparse
import pickle
import sys
sys.path.append('../../scripts')
from constant import *
from calc_MSE import deglat2m

height_b = 84.

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h", required=True, nargs="+", help="input files")
    parser.add_argument("--v", required=True, nargs="+", help="input files")
    parser.add_argument("--dir", required=True)
    #parser.add_argument("--rename", default=False, type=bool)

    args=parser.parse_args()
    
    print(args.h)
    print(args.v)

    h_ds = xr.open_mfdataset(args.h)
    v_ds = xr.open_mfdataset(args.v)
    
    h = h_ds['h']
    v = v_ds['v']
    
    if h.time != v.time:
        raise ValueError('time is not identical')
    xr.open_dataset
    hb = h.where(h.height >= height_b, drop=True)#.mean('height')
    vb = v.where(v.height >= height_b, drop=True)#.mean('height')

    hb = hb.where(hb.lon < 180., drop=True)
    vb = vb.where(vb.lon < 180., drop=True)
    
    dlat = vb.lat[2:].values - vb.lat[:-2].values
    dlat = deglat2m(dlat)
    dlat = dlat[np.newaxis, np.newaxis, :, np.newaxis]
    adv = vb[:,:,1:-1,:]*(hb[:,:,2:,:].values-hb[:,:,:-2,:].values) / dlat
    
    new_ds = xr.Dataset()
    new_ds['adv'] = adv
    new_ds['lat'] = np.round(new_ds.lat, 2)
    new_ds['lon'] = np.round(new_ds.lon, 2)
    
    num = args.v[0].split('/')[-1]
    num = num.split('_')[-1]
    print(num)
    new_ds.to_netcdf("data/"+args.dir+"/ke_var_adv_"+num)
    print(new_ds)