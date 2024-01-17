# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/10_viz.ipynb.

# %% auto 0
__all__ = ['plot_lines_with_param_color', 'plot_scatter_matrix', 'plot_train_diagnostics', 'sensitivity_plot']

# %% ../nbs/10_viz.ipynb 3
import warnings
warnings.simplefilter("ignore", UserWarning)
import seaborn

import numpy as np
import os
import matplotlib as mpl
import matplotlib.pylab as plt
import pandas as pd
import sepia.SepiaPlot as SepiaPlot
from sepia.SepiaModel import SepiaModel
from sepia.SepiaData import SepiaData
from matplotlib import ticker
from itertools import cycle
import matplotlib.colors as mcolors
import matplotlib.cm as cm

# %% ../nbs/10_viz.ipynb 4
def plot_lines_with_param_color(param_array:np.array=None, # parameter array
                                x_array:np.array=None, # x-axis array
                                y_array_all:np.array=None, # y-axis array
                                title_str:str=None, # Title string
                                xlabel_str:str=None, # x-label string
                                ylabel_str:str=None, # y-label string
                                param_name_str:str=None, # Parameter string
                               ):
    
    
    f, a = plt.subplots(1,1, figsize = (8, 5))  

    norm = mpl.colors.Normalize(vmin=param_array.min(), vmax=param_array.max())
    cmap = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.plasma)
    cmap.set_array([])

    for sim_index in range(param_array.shape[0]):
        a.plot(x_array, y_array_all[sim_index], 
                 '-', alpha= 0.5, c=cmap.to_rgba(param_array[sim_index]), 
                 label='Sim: '+str(sim_index) )

    # plt.plot(stellar_mass_test, gsmf_um_test, 'k.', label='UM z=0.00')
    a.set_xscale('log')
    # plt.axhline(y=0, linestyle='dashed', color='black')
    # plt.yscale('log')
    # plt.xlim(4e9, )
    # plt.ylim(-0.02, 0.02)

    clb = f.colorbar(cmap , ax=a)

    clb.ax.tick_params(labelsize=15) 
    clb.ax.set_title(param_name_str, fontsize=15)

    plt.title(title_str, fontsize=15)
    a.set_xlabel(xlabel_str, fontsize=15)
    a.set_ylabel(ylabel_str, fontsize=15)
    
    return f

# %% ../nbs/10_viz.ipynb 5
def plot_scatter_matrix(df, 
                        colors
                       ): 
    
    f, a = plt.subplots(1,1, figsize = (10, 10))
    scatter_matrix = pd.plotting.scatter_matrix(df, 
                                                color=colors,  
                                                figsize=(10,10), 
                                                alpha=1.0, 
                                                ax=a, 
                                                grid=False, 
                                                diagonal='hist',
                                                range_padding=0.1,
                                                s=80);

    for ax in scatter_matrix.ravel():
        ax.set_xlabel(ax.get_xlabel(), fontsize = 14, rotation = 0)
        ax.set_ylabel(ax.get_ylabel(), fontsize = 14, rotation = 90)
        
    return f

# %% ../nbs/10_viz.ipynb 6
def plot_train_diagnostics(sepia_model:SepiaModel=None, # Input data in SEPIA format, after PCA
                          ) -> tuple: #Pair-plot and Trace-plot
    samples_dict = sepia_model.get_samples()
    theta_pairs = SepiaPlot.theta_pairs(samples_dict)
    mcmc_trace = SepiaPlot.mcmc_trace(samples_dict)
    
    return theta_pairs, mcmc_trace

# %% ../nbs/10_viz.ipynb 7
def sensitivity_plot(k_all, # all wavenumbers
                     params_all, # all parameters
                     sepia_model, # SEPIA emulator model
                     emulator_function, # function which takes in sepia model and parameters
                     param_name, # Parameter name
                    ):

    color_by_index = 0
    colorparams = params_all[:, color_by_index]
    # colorparams = X_test_transformed1[:, color_by_index]
    colormap = cm.Dark2
    normalize = mcolors.Normalize(vmin=np.min(colorparams), vmax=np.max(colorparams))

    allMax = np.max(params_all, axis = 0)
    allMin = np.min(params_all, axis = 0)
    allMean = np.mean(params_all, axis = 0)

    numPlots = 100

    fig, ax = plt.subplots(5,1, figsize = (7, 15), sharex='col')
    plt.subplots_adjust(wspace=0.25)
    plt.subplots_adjust(hspace=0.05)
    plt.suptitle('Sensitivity analysis using emulator', fontsize=18, y=0.95)


    for paramNo in range(5):
            para_range = np.linspace(allMin[paramNo], allMax[paramNo], numPlots)        
            # colorList = plt.cm.coolwarm(np.linspace(0,1,numPlots))

            colormap = cm.coolwarm
            normalize = mcolors.Normalize(vmin=np.min(allMin[paramNo]), vmax=allMax[paramNo])

            for plotID in range(numPlots):
                    para_plot = np.copy(allMean)
                    para_plot[paramNo] = para_range[plotID]  #### allMean gets changed everytime!!

                    color = colormap(normalize(para_plot[paramNo]))

                    gsmf_decoded, _ = emulator_function(sepia_model, para_plot)

                    lineObj = ax[paramNo].plot(k_all, gsmf_decoded, lw= 1.5, color = color) 

                    # ax[paramNo].set_yscale('log')
                    ax[paramNo].set_xscale('log')
                    ax[paramNo].set_ylabel('B(k)', fontsize=18)
                    ax[paramNo].set_yticks([], minor = True)
                            
            
            # Colorbar setup
            s_map = cm.ScalarMappable(norm=normalize, cmap=colormap)
            s_map.set_array(colorparams)

            # If color parameters is a linspace, we can set boundaries in this way
            halfdist = (colorparams[1] - colorparams[0])/2.0
            boundaries = np.linspace(colorparams[0] - halfdist, colorparams[-1] + halfdist, len(colorparams) + 1)

            cbar = fig.colorbar(s_map, spacing='proportional', ax=ax[paramNo])

            cbarlabel = param_name[paramNo]
            cbar.set_label(cbarlabel, fontsize=20)

    ax[paramNo].set_xlabel('k[h/Mpc]', fontsize=18)
    plt.show()
