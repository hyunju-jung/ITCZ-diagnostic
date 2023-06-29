import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import glob
from matplotlib.ticker import MultipleLocator
import os
from itcztools import f_slope, find_fluxes

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

height_b = 84.
hm_1=84.
hm_2=67.

z_ifc=xr.open_dataset("../../z_ifc.nc")['z_ifc']
z_ifc=z_ifc.where(z_ifc.height_2 >= 25., drop=True)
z_full = 0.5*(z_ifc[:-1] + z_ifc[1:].values)
z_full = z_full.rename({'height_2':'height'})

if __name__ == "__main__":
    fig, axs = plt.subplots(3,3, figsize=(12,10), sharex=True)
    fig.subplots_adjust(wspace=0.45, hspace=0.25, bottom=0.15,left=0.1,
                        right=0.98, top=0.95)
    
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

        #Estimate ep and Mu
        ep=prec.values/(qv_h.values*(term1 - term2.values)+prec.values)
        Mu = 1/(1-ep.values)*(term1 - term2.values)
        
        #-----to print out quantitative values-------------------------
        weight = np.cos(np.radians(hb_hm.lat.values))
        weight = weight[np.newaxis, : , np.newaxis]

        print('---------ITCZ: %s---------' % od)
        print('prec: %.2f' %  (prec * weight * 86400.).sel(lat = slice(-5,5)).mean())
        print('<qv>: %.2f' %  (qv_h * weight *1000.).sel(lat = slice(-5,5)).mean())
        print('Mu: %.4f' %  (Mu * weight).sel(lat = slice(-5,5)).mean())
        print('ep: %.3f' %  (ep * weight).sel(lat = slice(-5,5)).mean())
        print('Fh: %.1f' %  (Fh * weight).sel(lat = slice(-10,10)).mean())
        #---------------------------------------------------------------

        #time and zonal mean for visualization
        ep_mean = np.nanmean(ep[0,...], axis=1)
        Mu_mean = Mu.mean(['time','lon'])
        hb_hm_mean = hb_hm.mean(['time','lon'])
        delta_S_mean = delta_S.mean(['time','lon'])
        Q_mean = Q.mean(['time','lon'])
        Fh_mean = Fh.mean(['time','lon'])

        x=hb_hm.lat

        term1 = term1.mean("lon")
        term2 = term2.mean("lon")
        prec_mean = prec.mean("lon")
        term3 = qv_h*1000.
        term3= term3.mean("lon")

        axs[0,0].plot(x,Fh_mean, color=colors[i], lw=lw, ls=ls[i], zorder=zo[i])

        axs[0,1].plot(x,Q_mean, color=colors[i], lw=lw, ls=ls[i], zorder=zo[i])
        axs[1,0].plot(x,hb_hm_mean*0.001,color=colors[i], lw=lw, ls=ls[i], zorder=zo[i])
        axs[1,1].plot(x,delta_S_mean,color=colors[i], label=labels[i], lw=lw, ls=ls[i], zorder=zo[i])

        axs[2,0].plot(x,term1[0,:], color=colors[i], lw=lw, ls=ls[i], zorder=zo[i])
        axs[2,1].plot(x,term2[0,:],color=colors[i], label=labels[i], lw=lw, ls=ls[i], zorder=zo[i])

        axs[0,2].plot(x,Mu_mean,color=colors[i], lw=lw, ls=ls[i], zorder=zo[i])

        axs[2,2].plot(x, term3[0,:], color=colors[i], lw=lw, ls=ls[i], zorder=zo[i])
        axs[1,2].plot(x, ep_mean, color=colors[i], lw=lw, ls=ls[i], zorder=zo[i])

    titles=['(a) Fh', '(d) Q','(g) Mu','(b) hb-hm','(e) S',
            '(h) '+r'$\epsilon_p$', '(c) Fh/(hb-hm)','(f) Q/S',
            '(i) $\langle$q'+r'$_{v}\rangle$']
            #'(i) (1-'+r'$\epsilon_p$'+')Mu']
    for i,ax in enumerate(axs.flat):
        ax.set_xlim(-20,20)
        ax.set_title(titles[i])
        ax.tick_params(axis='x')
        ax.tick_params(axis='y')
        ax.xaxis.set_minor_locator(MultipleLocator(5))
        
    xthicks = ['15\u00b0S','0\u00b0N','15\u00b0N']
    for i in range(3):
        axs[-1,i].set_xticks([-15,0,15])
        axs[-1,i].set_xticklabels(xthicks)

    axs[0,0].set_ylim(88,160)
    axs[0,0].set_ylabel('[W m'+r'$^{-2}$'+']')
    axs[0,1].set_ylim(0,0.03)
    axs[0,1].set_ylabel('[W m'+r'$^{-3}$'+']')
    axs[1,0].set_ylim(7,12)
    axs[1,0].set_ylabel('[kJ kg'+r'$^{-1}$'+']')
    axs[1,1].set_ylim(13,15)
    axs[1,1].set_ylabel('[J kg'+r'$^{-1}$ m'+r'$^{-1}$'+']')
    
    axs[2,0].set_ylim(0.008,0.016)
    axs[2,1].set_ylim(0,0.008)
    axs[2,2].set_ylim(2,4.5)
    axs[2,2].set_ylabel('[g kg$^{-1}$]')
    axs[2,0].set_ylabel('[kg m'+r'$^{-2}$'+' s'+r'$^{-1}$'+']')
    axs[2,1].set_ylabel('[kg m'+r'$^{-2}$'+' s'+r'$^{-1}$'+']')
    
    axs[0,2].set_ylim(0.01,0.06)
    axs[0,2].set_ylabel('[kg m'+r'$^{-2}$'+' s'+r'$^{-1}$'+']')
    axs[1,2].set_ylim(0.0,1.1)


    #sp_loc=['bottom','top','right','left']
    #for sp in sp_loc:
    #    axs[2,0].spines[sp].set_color('#377eb8')
    #    axs[2,1].spines[sp].set_color('#e41a1c')
    #    axs[2,2].spines[sp].set_color('#984ea3')
    #    for i in range(3):
    #        axs[2,i].spines[sp].set_linewidth(2.5)

    #axs[0,2].set_ylabel('[kg m'+r'$^{-2}$'+' s'+r'$^{-1}$'+']',fontsize=fs)
    #axs[0,2].set_ylabel('[mm day'+r'$^{-1}$'+']')

    axs[2,1].legend(loc='lower center', bbox_to_anchor=(0.5,-0.7),frameon=False, ncol=3)
    #plt.subplots_adjust(bottom = 0.05)

    #for i in range(3):
    #    axs[2,i].set_xlabel('lat',fontsize=fs)
    #    axs[2,i].set_xticks([-20,-10,0,10,20])

    plt.savefig('fig/ke_var_full.png')