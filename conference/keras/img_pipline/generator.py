import os
import math
import random
import numpy as np
from keras.preprocessing.image import load_img, img_to_array
from keras.utils import Sequence, to_categorical
from multiprocessing import Process, Queue


def scan_files(directory, prefix=None, postfix=None):
    files_list = []
    for root, sub_dirs, files in os.walk(directory):
        for special_file in files:
            if postfix:
                if special_file.endswith(postfix):
                    files_list.append(os.path.join(root, special_file))
            elif prefix:
                if special_file.startswith(prefix):
                    files_list.append(os.path.join(root, special_file))
            else:
                files_list.append(os.path.join(root, special_file))
    return files_list



class DataGenerator(Sequence):

    def __init__(self, directory, workers, target_size, batch_size, steps=None, shuffle=False):
        """ initialize image sequence generator 
        :param directory: the same as used in flow_from_directory
        :param workers: number of workers in data pipline
        :param target_size: image shape should be (target_size, target_size, 3)
        :param batch_size: batch size, int
        :param steps: number of batches to run in an epoch
        :param shuffle: flag to shuffle df rows at end of each epoch
        """
        self.directory = directory
        self.workers = workers
        self.target_size = target_size
        self.batch_size = batch_size
        self.steps = steps
        self.shuffle = shuffle

        n = workers * 2
        self.q_filenames = Queue(maxsize=n*batch_size)
        self.q_images = Queue(maxsize=n*batch_size)
        self.q_batches = Queue(maxsize=n)

        self.p_fileloaders = []
        self.p_imagereaders = []
        self.p_batchcollectors = []

        self.initialize()
        self.prepare()
        self.launch()



    def __bool__(self):
        return True


    def __len__(self):
        """ denotes the number of batches per epoch """
        return self.steps


    def __getitem__(self, index):

        while True:
            if not self.q_batches.empty():
                X, y = self.q_batches.get()
                break

        return X, y


    def initialize(self):
        self.classes = os.listdir(self.directory)
        self.classes.sort()
        self.num_classes = len(self.classes)
        self.class_indices = {class_i:i for i,class_i in enumerate(self.classes)}
        self.filenames = scan_files(self.directory)
        if self.shuffle:
            random.shuffle(self.filenames)
        self.samples = len(self.filenames)
        print("# files: ", self.samples)
        if self.steps is None:
            self.steps = math.ceil(self.samples / (self.batch_size))


    def prepare(self):
        self.p_fileloaders.append(Process(target=self.load_file))
        for i in range(self.workers):
            self.p_imagereaders.append(Process(target=self.read_image))
        self.p_batchcollectors.append(Process(target=self.collect_batch))


    def launch(self):
        all_processes = [self.p_fileloaders, self.p_imagereaders, self.p_batchcollectors]
        for ps in all_processes:
            for p in ps:
                p.start()

        # for ps in all_processes:
        #     for p in ps:
        #         p.join()


    def on_epoch_end(self):
        if self.shuffle:
            random.shuffle(self.filenames)
        self.load_file()


    def load_file(self): 
        for f in self.filenames:
            self.q_filenames.put(f)


    def read_image(self):
        while True:
            f = self.q_filenames.get()
            i = self.class_indices[os.path.basename(os.path.dirname(f))]
            img = load_img(f, target_size=self.target_size)
            img = img_to_array(img)
            self.q_images.put((img, i))


    def collect_batch(self):
        X = []
        y = []
        count = 0
        while True:
            img, i = self.q_images.get()
            X.append(img)
            y.append(i)
            count += 1
            if count == self.batch_size:
                X = np.asarray(X)
                y = np.asarray(y)
                y = to_categorical(y, num_classes=self.num_classes)
                
                self.q_batches.put((X,y))
                # print("collected one batch:", y)

                count = 0
                X = []
                y = []

