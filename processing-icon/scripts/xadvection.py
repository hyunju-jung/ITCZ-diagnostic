import xarray as xr
import glob
import numpy as np
import argparse
import pickle
import sys
sys.path.append('../../scripts')
from constant import *
from calc_MSE import deglat2m, deglon2m
from horizontal_interpolation import get_interpolator

height_b = 84.

src_grid='/archive/meteo/w2w-p2/B6/DA/13km/grid_DOM01.nc'
ifunc = get_interpolator(src_grid, "weights.pkl")

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h", required=True, nargs="+", help="input files")
    parser.add_argument("--wind", required=True, nargs="+", help="input files")
    parser.add_argument("--dir", required=True)
    #parser.add_argument("--rename", default=False, type=bool)

    args=parser.parse_args()

    h = xr.open_mfdataset(args.h)['h']
    v = xr.open_mfdataset(args.wind)['v']
    u = xr.open_mfdataset(args.wind)['u']
    
    if h.time != v.time:
        raise ValueError('time is not identical')
    
    hb = h.where(h.height >= height_b, drop=True)#.mean('height')
    ub = u.where(u.height >= height_b, drop=True)#.mean('height')
    vb = v.where(v.height >= height_b, drop=True)#.mean('height')
    
    vb = ifunc(vb)
    vb['lat'] = np.round(vb.lat,2)
    ub = ifunc(ub)
    ub['lat'] = np.round(ub.lat,2)

    hb = hb.where(hb.lon < 180., drop=True)
    vb = vb.where(vb.lon < 180., drop=True)
    ub = vb.where(ub.lon < 180., drop=True)

    dlat = vb.lat[2:].values - vb.lat[:-2].values
    dlat = deglat2m(dlat)
    dlat = dlat[np.newaxis, np.newaxis, :, np.newaxis]
    adv_y = vb[:,:,1:-1,:]*(hb[:,:,2:,:].values-hb[:,:,:-2,:].values) / dlat
    
    dlon = vb.lon[2:].values - vb.lon[:-2].values
    #dlon = deglon2m(dlon,vb.lat[1:-1])
    dlon = dlon[np.newaxis, np.newaxis, np.newaxis, :]
    adv_x = ub[:,:,:,1:-1]/np.cos(np.radians(vb.lat))*(hb[:,:,:,2:].values-hb[:,:,:,:-2].values) / (a*dlon)

    print(adv_y)
    print(adv_x)
    
    adv = adv_y[:,:,:,1:-1] + adv_x[:,:,1:-1,:].values
    
    new_ds = xr.Dataset()
    new_ds['adv_y'] = adv_y[:,:,:,1:-1]
    new_ds['adv_x'] = adv_x[:,:,1:-1,:]
    new_ds['adv'] = adv
    num = args.wind[0].split('/')[-1]
    num = num.split('_')[-1]
    print(num)
    new_ds.to_netcdf("data/"+args.dir+"/ke_var_adv_"+num)
    print(new_ds)
