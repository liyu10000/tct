from keras.models import *
from keras.layers import *
from keras.applications import *
from keras.preprocessing.image import *
from keras import optimizers
from keras.applications.vgg19 import preprocess_input
from keras.utils.training_utils import multi_gpu_model
from keras.utils import to_categorical
import tensorflow as tf



class PredictModel:

    def __init__(self, gpu_num=4)
        self.gpu_num = gpu_num


    def build_model(self):
        with tf.device('/cpu:0'):
            input_tensor = Input((128, 128, 512))
            
            conv1_1 = Conv2D(filters = 1024, kernel_size = (3, 3), strides = (1, 1),
                           activation='relu', padding='same', name='conv1_1')(input_tensor)
            conv1_2 = Conv2D(filters = 1024, kernel_size = (1, 1), strides = (1, 1),
                           activation='relu', padding='same', name='conv1_2')(conv1_1)
            mp1 = MaxPooling2D(pool_size=(2, 2), strides=2, padding='same')(conv1_2)
            
            conv2_1 = Conv2D(filters = 2048, kernel_size = (3, 3), strides = (1, 1),
                           activation='relu', padding='same', name='conv2_1')(mp1)
            conv2_2 = Conv2D(filters = 2048, kernel_size = (1, 1), strides = (1, 1),
                           activation='relu', padding='same', name='conv2_2')(conv2_1)
            mp2 = MaxPooling2D(pool_size=(2, 2), strides=2, padding='same')(conv2_2)
            
            conv3_1 = Conv2D(filters = 4096, kernel_size = (3, 3), strides = (1, 1),
                           activation='relu', padding='same', name='conv3_1')(mp2)
            conv3_2 = Conv2D(filters = 2048, kernel_size = (1, 1), strides = (1, 1),
                           activation='relu', padding='same', name='conv3_2')(conv3_1)
            mp3 = MaxPooling2D(pool_size=(2, 2), strides=2, padding='same')(conv3_2)
            
            conv4_1 = Conv2D(filters = 4096, kernel_size = (3, 3), strides = (1, 1),
                           activation='relu', padding='same', name='conv4_1')(mp3)
            conv4_2 = Conv2D(filters = 2048, kernel_size = (1, 1), strides = (1, 1),
                           activation='relu', padding='same', name='conv4_2')(conv4_1)
            mp4 = MaxPooling2D(pool_size=(2, 2), strides=2, padding='same')(conv4_2)
            
            conv5_1 = Conv2D(filters = 4096, kernel_size = (3, 3), strides = (1, 1),
                           activation='relu', padding='same', name='conv5_1')(mp4)
            conv5_2 = Conv2D(filters = 2048, kernel_size = (1, 1), strides = (1, 1),
                           activation='relu', padding='same', name='conv5_2')(conv5_1)

            gmp = GlobalMaxPooling2D()(conv5_2)
            drop = Dropout(0.5, name='drop_fc1')(gmp)
            predictions = Dense(2, activation='softmax')(drop)

            model = Model(inputs=input_tensor, outputs=predictions)
            # model.load_weights('diagnosis.h5')
            # model.summary()

        self.model = multi_gpu_model(model, gpus=self.gpu_num)


    def load_weights(self, weights_path):
        self.model.load_weights(weights_path)


    def predict(self, features, batch_size=4, verbose=1):
        return self.model.predict(features, batch_size=batch_size, verbose=verbose)
