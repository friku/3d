#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 20:10:32 2019

@author: fujimoto
"""

import binvox_rw
import scipy.ndimage
import os 
import numpy as np
import utils



def saveModel(data,save_dir,sample_batch_size,it):
    file_path = "./1a0c94a2e3e67e4a2e4877b52b3fca7.binvox"
    with open(file_path, 'rb') as f:
        model = binvox_rw.read_as_3d_array(f)
        divide = 4
        model.dims=[model.dims[0]//divide,model.dims[1]//divide,model.dims[2]//divide]
        model.scale = model.scale/divide
        data = data.astype("bool")
        data = np.reshape(data, [sample_batch_size] + model.dims)
#        print(data[0])
        for i in range(sample_batch_size):
            filename = str(it)+'_'+str(i) +'.binvox'
            print(data[i].shape)
            
            model.data = data[i]
            print(model.data.shape)
            with open(save_dir+'/'+filename, mode='w') as f_test:
                model.write(f_test)

data = np.load("3dDataInt.npy")
save_dir = './data_view'
utils.mkdir(save_dir + '/')
utils.saveModel(data,save_dir,100,1)