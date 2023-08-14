import xarray as xr
import glob
import numpy as np
import argparse
import sys
sys.path.append('../../scripts')
from constant import *

height_b = 84.
rho=1.2

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    #parser.add_argument("--source", required=True, nargs="+", help="input files")
    parser.add_argument("--dir", required=True)
    #parser.add_argument("--rename", default=False, type=bool)

    args=parser.parse_args()

    z_ifc = xr.open_dataset('/project/meteo/w2w/B6/Hyunju/z_ifc.nc')['z_ifc']
    z_ifc = z_ifc.rename({'height_2':'height'})
    z_ifc = z_ifc.where(z_ifc.height >= height_b, drop=True)
    dz = z_ifc[:-1] - z_ifc[1:].values
    
    ofiles = glob.glob('data/%s/ke_var_adv_????.nc' % args.dir)
    ofiles = sorted(ofiles)
    
    ds = xr.open_mfdataset(ofiles)
    ADV = rho*ds.adv*dz
    ADV = ADV.sum('height')
    ADV = ADV.mean('time')

    new_ds = xr.Dataset()
    new_ds['adv'] = ADV
    
    new_ds.to_netcdf("data/"+args.dir+"/ke_var_ADV_avg.nc")
    print(new_ds)