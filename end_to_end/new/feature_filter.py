from keras.models import *
from keras.layers import *
from keras.applications import *
from keras.preprocessing.image import *
from keras import optimizers
from keras.applications.vgg19 import preprocess_input
from keras.utils.training_utils import multi_gpu_model
import tensorflow as tf
import cv2
import os

from common.utils import ImageSlice, ImageSliceInMemory

class FeatureFilter(object):
    """docstring for FeatureExtrctor"""
    def __init__(self, gpu_num = 1, gpus = "0"):
        self.gpu_num = gpu_num
        self.gpus = gpus

        self.model = None

    def build_model(self):
        os.environ["CUDA_VISIBLE_DEVICES"] = self.gpus
        with tf.device('/cpu:0'):

        # build base model body
            input_tensor = Input((224, 224, 3))
            x = Lambda(vgg19.preprocess_input)(input_tensor)
        
            base_model = VGG19(input_tensor=x, weights=None, include_top=False)
        
        # build temp model for weights assign
            m_out = base_model.output
            flatten = Flatten(name='flatten')(m_out)
            fc1 = Dense(4096, activation='relu', name='fc1')(flatten)
            drop_fc1 = Dropout(1.0, name='drop_fc1')(fc1)
            fc2 = Dense(512, activation='relu', name='fc2')(drop_fc1)
            drop_fc2 = Dropout(1.0, name='drop_fc2')(fc2)
            predictions = Dense(2, activation='softmax', name='predictions')(drop_fc2)
            
            model_weights = Model(inputs=base_model.input, outputs=predictions)
            model_weights.load_weights("vgg19_finetune.h5")
        
        # build real model for feature extraction
            input_tensor_filter = Input(shape = (512, ))
            drop_fc2 = Dropout(1.0, name='drop_fc2')(input_tensor_filter)
            predictions = Dense(2, activation='softmax', name='predictions')(drop_fc2)

            model = Model(inputs=input_tensor_filter, outputs=predictions)

            pretrained_weights = model_weights.get_layer(index=27).get_weights()
            print("du", model_weights.get_layer(index=27).name)
            model.get_layer(index=1).set_weights(pretrained_weights)
            print("du", model.get_layer(index=1).name)
            pretrained_weights = model_weights.get_layer(index=28).get_weights()
            print("du", model_weights.get_layer(index=28).name)
            model.get_layer(index=2).set_weights(pretrained_weights)
            print("du", model.get_layer(index=2).name)

            model.summary()
        
        parallel_model = multi_gpu_model(model, gpus = self.gpu_num)
        #parallel_model.summary()

        print("    build completed!")

        self.model = parallel_model

    def feature_filter(self, features):
        features = features.reshape(128*128, 512)
        result_all = self.model.predict(features, batch_size=512, verbose=0)

        abnormal = 0
        normal = 0

#        for result in result_all:
#            if result[0] > 0.95:
#                abnormal = abnormal + 1
#            else:
#                normal = normal + 1

#        print("du", "abnormal:", abnormal, "normal:", normal)

        for i, feature in enumerate(features):
        	if (result_all[i][0] < 0.95):
        		features[i] = np.zeros((512))

        features = features.reshape(128,128, 512)

        return features

        

