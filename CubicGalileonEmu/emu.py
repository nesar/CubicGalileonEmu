# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_emu.ipynb.

# %% auto 0
__all__ = ['blockPrint', 'enablePrint', 'emulate', 'load_model_multiple', 'emu_redshift']

# %% ../nbs/03_emu.ipynb 3
from sepia.SepiaModel import SepiaModel
from sepia.SepiaData import SepiaData
from sepia.SepiaPredict import SepiaEmulatorPrediction
# from sepia.SepiaPredict import SepiaFullPrediction
# from sepia.SepiaPredict import SepiaXvalEmulatorPrediction
# from sepia.SepiaSharedThetaModels import SepiaSharedThetaModels
import numpy as np
from .pca import do_pca
from .gp import gp_load
from .load import sepia_data_format
import sys
import os

# %% ../nbs/03_emu.ipynb 4
def blockPrint():
    sys._jupyter_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys._jupyter_stdout = sys.stdout
    sys.stdout = sys.__stdout__

# %% ../nbs/03_emu.ipynb 5
def emulate(sepia_model:SepiaModel=None, # Input data in SEPIA format
        input_params:np.array=None, #Input parameter array 
       ) -> tuple: # 2 np.array of mean and (0.05,0.95) quantile in prediction
    
    
    if len(input_params.shape) == 1:
        ip = np.expand_dims(input_params, axis=0)
        
    else:
        ip = input_params
        
    pred_samples= sepia_model.get_samples(numsamples=10)
        
    pred = SepiaEmulatorPrediction(t_pred=ip, samples=pred_samples, model=sepia_model)
    
    pred_samps = pred.get_y()
    
    pred_mean = np.mean(pred_samps, axis=0).T
    pred_err = np.quantile(pred_samps, [0.05, 0.95], axis=0).T
    
    return pred_mean, pred_err

# %% ../nbs/03_emu.ipynb 6
def load_model_multiple(model_dir:str=None, # Pickle directory path
                        p_train_all:np.array=None, # Parameter array
                        y_vals_all:np.array=None, # Target y-values array
                        y_ind_all:np.array=None, # x-values
                        z_index_range:np.array=None, # Snapshot indices for training
                        sepia_model_i:str=None,
                   ) -> None: 
    
    blockPrint()
    
    model_list = []
    
    for z_index in z_index_range:
        
        sepia_data = sepia_data_format(p_train_all, y_vals_all[:, z_index, :], y_ind_all)

        print(sepia_data)
        sepia_model_i = do_pca(sepia_data, exp_variance=0.95)
        
        model_filename = model_dir + 'multivariate_model_z_index' + str(z_index) 
        sepia_model_z = gp_load(sepia_model_i, model_filename)
        model_list.append(sepia_model_z)

    enablePrint()

    print('Number of models loaded: ' + str(len(model_list))  )


    return model_list
 

# %% ../nbs/03_emu.ipynb 7
def emu_redshift(input_params_and_redshift:np.array=None, # Input parameters (along with redshift) 
                 sepia_model_list:list=None,
                 z_all:np.array=None): # All the trained models
    
    z = input_params_and_redshift[:, -1]
    input_params = input_params_and_redshift[:, :-1]
       
    '''
    if (z == 0):
        # No redshift interpolation for z=0
        GPm, PCAm = model_load(snap_ID=LAST_SNAP, nRankMax=DEFAULT_PCA_RANK)
        Pk_interp = emulate(sepia_model, input_params)
        
        
    else:
    '''
    
    # Linear interpolation between z1 < z < z2
    snap_idx_nearest = (np.abs(z_all - z)).argmin()
    if (z > z_all[snap_idx_nearest]):
        snap_ID_z1 = snap_idx_nearest - 1
    else:
        snap_ID_z1 = snap_idx_nearest
    snap_ID_z2 = snap_ID_z1 + 1
    

    sepia_model_z1 = sepia_model_list[snap_ID_z1]
    Bk_z1, Bk_z1_err = emulate(sepia_model_z1, input_params)
    z1 = z_all[snap_ID_z1]
    

    sepia_model_z2 = sepia_model_list[snap_ID_z2]
    Bk_z2, Bk_z2_err = emulate(sepia_model_z2, input_params)
    z2 = z_all[snap_ID_z2]

    Bk_interp = np.zeros_like(Bk_z1)
    Bk_interp = Bk_z2 + (Bk_z1 - Bk_z2)*(z - z2)/(z1 - z2)

    Bk_interp_err = np.zeros_like(Bk_z1_err)
    Bk_interp_err = Bk_z2_err + (Bk_z1_err - Bk_z2_err)*(z - z2)/(z1 - z2)
    
    return Bk_interp, Bk_interp_err
