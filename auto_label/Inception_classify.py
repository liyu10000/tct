from keras.models import *
from keras.layers import *
from keras.applications import *
from keras.preprocessing.image import *
import numpy as np

# 6 classes
model_path = "model6_api_0812.h5"
weights_file = "weights.03-0.2672.hdf5"

# 14 classes


# def inception_init():
#     base_model = InceptionV3(weights=None, include_top=False)
#     x = base_model.output
#     x = GlobalAveragePooling2D()(x)
#     x = Dense(FC_SIZE, activation='relu')(x) #new FC layer, random init
#     predictions = Dense(nb_classes, activation='softmax')(x) #new softmax layer
#     model = Model(inputs=base_model.input, outputs=predictions)
#     model.load_weights(weights_file)
#     return model

def inception_init():
    model = load_model(model_path)
    model.load_weights(weights_file)
    return model

def inception_predict(img_data, batch_size, model):

    predictions = []
    batches = int(len(img_data) / batch_size) + 1

    for i in range(batches):
        batch_data =  img_data[i * batch_size : (i + 1) * batch_size]
        predictions.extend(model.predict_on_batch(batch_data))

    return np.asarray(predictions)
