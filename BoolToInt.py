import binvox_rw
import scipy.ndimage
import os 
import numpy as np

data = np.load("3dData.npy")
print(data.shape)
print(data[0])

_data = data.astype('int8')
print(_data)
print(_data.shape)

np.save("3dDataInt.npy",_data)
