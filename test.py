import binvox_rw
import scipy.ndimage
import os 
import numpy as np


def resizevox(model,divide):
    model.dims=[model.dims[0]//divide,model.dims[1]//divide,model.dims[2]//divide]
    model.scale = model.scale/divide
    model.data = model.data[::divide,::divide,::divide]

    return model

def modelInfo(model):
    print(model.dims)
    print(model.scale)
    print(model.translate)
    print(model.data.shape)

file_path = "/home/riku/binvox-rw-py/models-binvox/"
file_list = os.listdir(file_path)

modelnpy = []
for file_name in file_list[:10]:
    with open(file_path + file_name, 'rb') as f:
        model = binvox_rw.read_as_3d_array(f)
        resizevox(model,4)
        modelInfo(model)
        modelnpy.append(model.data)


data = np.load("3dData.npy")
print(data.shape)
file_name = "test.binvox"

model.data = data[0]
with open('/home/riku/binvox-rw-py/resize_models/'+file_name, mode='w') as f_test:
    # scipy.ndimage.binary_dilation(model.data.copy(), output=model.data)
    model.write(f_test)