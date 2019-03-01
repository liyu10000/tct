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

class FeatureExtrctor(object):
    """docstring for FeatureExtrctor"""
    def __init__(self, gpu_num = 1, gpus = "0"):
        self.gpu_num = gpu_num
        self.gpus = gpus

        self.model = None

        self.pics = None

    def build_model(self, weights_path):
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
            model_weights.load_weights(weights_path)
        
        # build real model for feature extraction
            m_out = base_model.output
            flatten = Flatten(name='flatten')(m_out)
            fc1 = Dense(4096, activation='relu', name='fc1')(flatten)
            drop_fc1 = Dropout(1.0, name='drop_fc1')(fc1)
            fc2 = Dense(512, activation='relu', name='fc2')(drop_fc1)
            drop_fc2 = Dropout(1.0, name='drop_fc2')(fc2)
            model = Model(inputs=base_model.input, outputs=drop_fc2)

            for i in range(28):
                pretrained_weights = model_weights.get_layer(index=i).get_weights()
                # print(model_weights.get_layer(index=i).name)
                model.get_layer(index=i).set_weights(pretrained_weights)
                
            model.summary()
        
        parallel_model = multi_gpu_model(model, gpus = self.gpu_num)
        #parallel_model.summary()

        print("    build completed!")

        self.model = parallel_model

    def read_big_pic(self, pic_path):
        print(pic_path)
        worker = ImageSliceInMemory(pic_path)
        err , results = worker.get_slices()

        if (0 == err):
#            pics_dict = {}

#            for i in range(128*128):
#                pics_dict[str(results[i]['x']) + "_" + str(results[i]['y'])] = results[i]['image']
            
            pics_dict = results

            pics = []
            sorted_keys = sorted(pics_dict.keys())
            for key in sorted_keys:
                pics.append(pics_dict[key])

            pics = np.asarray(pics)

            self.pics = pics

        else:
            self.pics = None

        return err

    def feature_extrctor(self):
        result_all = self.model.predict(self.pics, batch_size=128, verbose=1)
        result_all = np.asarray(result_all)
        result_all_format = result_all.reshape(128,128, 512)

        return result_all_format

        

