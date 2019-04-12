import h5py
import random
import numpy as np
from keras.utils import Sequence, to_categorical
from keras.utils.io_utils import HDF5Matrix
# from keras.preprocessing.image import ImageDataGenerator



class DataGenerator(Sequence):
    def __init__(self, hdf5_file, datasets, augmentor, batch_size, steps=None, shuffle=False):
        self.augmentor = augmentor
        self.batch_size = batch_size
        self.shuffle = shuffle

        f = h5py.File(hdf5_file)
        self.image = f[datasets[0]]  # image dataset keyword: image
        self.label = f[datasets[1]]  # label dataset keyword: label
        assert self.image.shape[0] == self.label.shape[0]
        self.samples = self.image.shape[0]
        print("# files found: ", self.samples)
        self.steps = self.samples // self.batch_size


    def __bool__(self):
        return True


    def __len__(self):
        """ denotes the number of batches per epoch """
        return self.steps


    def __getitem__(self, index):
        slice_ = [index*self.batch_size, (index+1)*self.batch_size]

        X = self.image[slice_[0]:slice_[1]]
        X = np.asarray([self.augmentor.random_transform(x, seed=index) for x in X])  # data augmentation
        y = self.label[slice_[0]:slice_[1]]

        return X, y


    def on_epoch_end(self):
        pass

