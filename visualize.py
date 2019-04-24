import binvox_rw
import scipy.ndimage



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

with open('./models-binvox-solid/6fa63f7d098b3c6228a1548e344f0e2e.binvox', 'rb') as f:
    model = binvox_rw.read_as_3d_array(f)
    modelInfo(model)
    resizevox(model,1)
    modelInfo(model)

    # print(model.dims)
    # print(model.scale)
    # print(model.translate)
    print(model.data)

    # print(model.data.shape)


    

    with open('testresize2.binvox', mode='w') as f_test:
        # scipy.ndimage.binary_dilation(model.data.copy(), output=model.data)
        model.write(f_test)