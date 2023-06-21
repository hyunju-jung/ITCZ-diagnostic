import xarray as xr
from matplotlib.colors import TwoSlopeNorm
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from matplotlib.ticker import MultipleLocator
import os
import sys
sys.path.append("../../scripts")
from atm_var import ms_v

def ind_max(a):
    return np.unravel_index(np.argmax(a, axis=None), a.shape)

def ind_min(a):
    return np.unravel_index(np.argmin(a, axis=None), a.shape)

np.set_printoptions(suppress=True)

HOME=os.path.expanduser("~")
opath='%s/B6/Hyunju/mse-budget/conceptual-model/data/' % HOME
flists=['param', 'explicit', 'shallow','stochastic_shallow', 
        'P5', 'E5']
titles=['(a) P13', '(b) E13', '(c) S13', '(d) SS13', '(e) P5', '(f) E5']

z_ifc=xr.open_dataset('../../z_ifc.nc')['z_ifc']
dz=z_ifc[:-1].values - z_ifc[1:].values
z_full=z_ifc[1:].values + dz*0.5

n1=5
n2=10
plt.rcParams.update({'font.size': 18})

fig, axs = plt.subplots(2,4,figsize=(13,7), sharey=True)
axs = axs.flat
plt.subplots_adjust(top=0.82, left=0.065, right=0.90, bottom=0.13, wspace=0.08, hspace=0.155)

clev = np.linspace(-15,15,7)
cflev=np.linspace(-10,35,19)

axs[0].set_yticks([0,5,10])
axs[0].yaxis.set_minor_locator(MultipleLocator(2.5))
axs[0].set_ylabel('z [km]')
axs[4].set_ylabel('z [km]')

#new color map
new_colors =["#301437", "#301437", "#32113D", "#3E1150", "#4C1669", "#562284", "#5C3499",
             "#5E47A7", "#5F59B1", "#606DB8", "#647EBC", "#6C8FBF", "#799EC1",
             "#8AAEC5", "#A0BCC9", "#B7C9D0", #"#CED3D9",
             "#D8C7BE", "#C27C62", "#983550","#4A1342"]
new_colors = new_colors[1:]

new_cmap = mpl.colors.ListedColormap( new_colors[::-1] )
new_cmap.set_over(new_colors[-1])
new_cmap.set_under(new_colors[0])

for i, od in enumerate(flists):
    axs[i].set_title(titles[i], loc='left')
        
    u=xr.open_dataset('%s/%s/obs_DOM01_ML_reg_u_timeavg.nc' % (opath, od))['u']
    u=u.mean('lon')
    
    v=xr.open_dataset('%s/%s/obs_DOM01_ML_reg_v_timeavg.nc' % (opath, od))['v']
    v=v.mean('lon')

    #---Zonal wind---
    divnorm = TwoSlopeNorm(vmin=-10., vcenter=0, vmax=35)
    im = axs[i].contourf(u.lat, z_full*0.001, u[0,...], levels=cflev,
                 cmap=new_cmap, extend='max')
    
    #---------mass stream function----------    
    pres = xr.open_dataset(opath+od+'/obs_DOM01_ML_reg_pres_timeavg.nc')["pres"]
    pres = pres.mean('lon')

    msf = ms_v(v, pres, v.lat)
        
    cs=axs[i].contour(v.lat, z_full*0.001, msf[0,:,:]*1e-10, cmap="coolwarm", linewidths=3, levels=clev)
    axs[i].clabel(cs, inline=False, fmt='%1.1f')
    
    ind = ind_max(msf)
    print("max %.2f at %.2f deg at lev %.2f" %(msf[ind],v.lat[ind[-1]],z_full[ind[1]]*0.001))
    

axs[0].set_yticks([0,5,10])

axs[-1].remove()
axs[-2].remove()

xthicks = ['15\u00b0S','0\u00b0','15\u00b0N']
for i in range(6):
    axs[i].set_ylim(0,13)
    axs[i].set_xlim(-20.,20)
    axs[i].set_xticks([-15,0,15])
    axs[i].set_xticklabels(xthicks)
    axs[i].xaxis.set_minor_locator(MultipleLocator(5))

axs[0].set_xticklabels([])
axs[1].set_xticklabels([])

#cbaxes = fig.add_axes([0.93, 0.22, 0.015, 0.5])
#cb=fig.colorbar(im, cax = cbaxes, ticks=cflev[::4])
#fig.text(0.905, 0.765, 'u [m s'+r'$^{-1}$'+']', va='center')

cbaxes = fig.add_axes([0.5, 0.34, 0.4, 0.02])
cb=fig.colorbar(im, cax = cbaxes, ticks=cflev[::4], orientation='horizontal')
fig.text(0.68, 0.39, '[m s'+r'$^{-1}$'+']', va='center')

#plt.savefig("fig/u_mass_stream_darkbluemode.png", facecolor='#1d305f',dpi=100)
plt.savefig("fig/u_mass_stream_high_res.png", dpi=100)