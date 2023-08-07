import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from enstools.io import read
from matplotlib.ticker import MultipleLocator
import pandas as pd
import glob
import pickle
import os
from itcztools import f_slope, find_fluxes

np.set_printoptions(suppress=True)
plt.rcParams.update({'font.size': 18})
opath="/archive/meteo/w2w-p2/B6"
opath2="../../mse-budget/conceptual-model/data"
flists=['param','explicit','shallow','stochastic_shallow','P5','E5']

np.set_printoptions(suppress=True)

colors = ['black','#E51932','#1AB2FF','#654CFF','#8D8D8D','#FF99BF']
labels=['P13','E13','S13','SS13','P5','E5']
lw=2
ls = list(['solid'])*4 + list(['dashdot'])*2
zo=[0,3,1,2,4,5]

height_b = 84. #86.: limits for the shallowest BL height
hm_1=84.
hm_2=67.

z_ifc=xr.open_dataset("../../z_ifc.nc")['z_ifc']
z_ifc=z_ifc.where(z_ifc.height_2 >= 25., drop=True)
z_full = 0.5*(z_ifc[:-1] + z_ifc[1:].values)
z_full = z_full.rename({'height_2':'height'})

if __name__ == "__main__":
    fig, axs = plt.subplots(1,3, figsize=(12,3.8), sharex=True)
    fig.subplots_adjust(wspace=0.4, hspace=0.25, bottom=0.25,left=0.08,right=0.98)
    
    for i, od in enumerate(flists):
        #obtain Fh
        Fh = find_fluxes(od, ['alhfl_s','ashfl_s'])
        
        #obtain hb-hm
        h = xr.open_dataset("%s/%s/ke_var_timeavg.nc" % (opath2, od))['h']
        s = xr.open_dataset("%s/%s/ke_var_timeavg.nc" % (opath2, od))['s']

        hb = h.where(h.height >= height_b, drop=True).mean('height')
        hm = h.where( ( h.height <= height_b ) & ( h.height >= hm_2 ), drop=True).mean('height')

        hb_hm = (hb - hm)
        
        #obtain radiative cooling
        rad=xr.open_dataset('%s/%s/rad_timeavg.nc' % (opath2, od))
        Q = -(rad.lwrad + rad.swrad)
        Q = Q.where((Q.height <= hm_1) & (Q.height >= hm_2), drop=True).mean('height')

        #obtain dry stability
        z_in=z_full.where((z_full.height <= hm_1) & (z_full.height >= hm_2), drop=True)
        s_in=s.where((s.height <= hm_1) & (s.height >= hm_2), drop=True)

        slope=f_slope(z_in.values[np.newaxis, : , np.newaxis, np.newaxis], s_in, ax=1)
        slope=xr.DataArray(slope, coords=[s.time, s.lat, s.lon], dims=['time','lat','lon'])
        delta_S=slope.copy() + 9.8 #*dz

        #calculating the terms in the paranthesis 
        term1=Fh.values/hb_hm
        term2=Q.values/delta_S
        
        #need prec to obtain Mu and ep
        ofiles = glob.glob('%s/%s/obs_DOM01_ML_reg_tot_prec_*.nc' % (opath2, od))
        ofiles = sorted(ofiles)

        prec=xr.open_mfdataset([ofiles[0], ofiles[-1]])["tot_prec"]
        prec = prec.diff('time')/(40.*86400) # mm/s
        prec = prec.where(prec.lon < 180., drop=True)

        #need <qv> to obtain Mu and ep
        obs_ds = xr.open_dataset("%s/%s/nature_run_DOM01_ML_timeavg.nc" % (opath2, od))
        obs_ds = obs_ds.where(obs_ds.lon < 180., drop=True)

        tqv = obs_ds['tqv']
        pres_sfc = obs_ds['pres_sfc']
        qv_h = tqv/pres_sfc*9.8

        #Including advection term!
        adv = xr.open_dataset("%s/%s//ke_var_ADV_avg.nc" % (opath2, od))['adv']
        Fh_a = Fh[0,1:-1,:].copy()
        hb_hm_a = hb_hm[0,1:-1,:].values.copy()
        prec_a = prec[0,1:-1,:].values.copy()
        qv_h_a = qv_h[0,1:-1,:].values.copy()

        print(Fh_a.shape, adv.shape)

        term1_adv = (Fh_a - adv.values)/hb_hm_a
        ep_adv=prec_a/(qv_h_a*(term1_adv - term2[0,1:-1,:].values)+prec_a)
        Mu_adv = 1/(1-ep_adv)*(term1_adv - term2[0,1:-1,:].values)

        weight = np.cos(np.radians(h.lat[1:-1].values))
        weight = weight[ : , np.newaxis]
        
        print('---------ITCZ: %s---------' % od)
        #print('Mu: %.4f' %  (Mu_adv * weight).sel(lat = slice(7,17)).mean())
        #print('Mu: %.4f' %  (Mu_adv * weight).sel(lat = slice(-17,-7)).mean())
        #print('ep: %.3f' %  (ep_adv * weight).sel(lat = slice(7,17)).mean())
        #print('ep: %.3f' %  (ep_adv * weight).sel(lat = slice(-17,-7)).mean())
        print('adv: %.3f' %  (adv * weight).sel(lat = slice(-20,20)).mean())
        #print('adv: %.3f' %  (adv * weight).sel(lat = slice(-20,-5)).mean('lon').max())


        axs[0].plot(h.lat[1:-1], adv.mean(['lon']), color=colors[i], lw=lw, ls=ls[i], zorder=zo[i])
        axs[2].plot(h.lat[1:-1], Mu_adv.mean(['lon']),color=colors[i], lw=lw, ls=ls[i], zorder=zo[i])
        axs[1].plot(h.lat[1:-1], ep_adv.mean(['lon']),color=colors[i], lw=lw, label=labels[i], ls=ls[i], zorder=zo[i])

    xthicks = ['15\u00b0S','0\u00b0N','15\u00b0N']
    titles=['(a) Adv', '(b) '+r'$\epsilon_p$', '(c) M$_\mathrm{u}$']
            #'(i) (1-'+r'$\epsilon_p$'+')Mu']
    for i,ax in enumerate(axs):
        ax.set_xlim(-20,20)
        ax.set_title(titles[i])
        ax.tick_params(axis='x')
        ax.tick_params(axis='y')
        ax.set_xticks([-15,0,15])
        ax.set_xticklabels(xthicks)
        ax.xaxis.set_minor_locator(MultipleLocator(5))

    axs[0].set_ylim(-5,40)
    axs[0].set_ylabel('[W m'+r'$^{-2}$'+']')
    axs[2].set_ylim(0.005,0.05)
    axs[2].set_yticks(np.arange(1,6,1)*0.01)
    axs[2].set_ylabel('[kg m'+r'$^{-2}$'+' s'+r'$^{-1}$'+']')
    axs[1].legend(loc='lower center', bbox_to_anchor=(0.5,-0.5),frameon=False, ncol=3)
    axs[1].set_yticks(np.arange(0,1.1,0.25))
    axs[1].set_ylim(0.0,1.1)

    plt.savefig('fig/ke_var_fig3.png', dpi=100)