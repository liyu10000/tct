import os
import cv2
import h5py
import random
import numpy as np
from datetime import datetime
from keras.utils import to_categorical
from sklearn.preprocessing import MultiLabelBinarizer
from multiprocessing import Process, Queue


# class_index = {'n':0, 'p':1}
image_size = 299
batch_size = 64
n_channels = 3
num_classes = 13
multi_label = True  # use multi label or not
num_workers = 8  # number of image loaders

data_path = "/home/ssd_array0/Data/batch6.4_1216/train-gnet2.txt"
save_file = "/home/hdd_array0/Data/hdf5/train-gnet2.hdf5"
append = False  # append to existed dataset
i_key = "image"  # keyword to image dataset
l_key = "label"  # keyword to label dataset



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


def process(image):
    hlsImg = image.astype(np.float32)
    hlsImg = hlsImg / 255.0
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_RGB2HLS)
    hlsImg[:, :, 2] = 1.5 * hlsImg[:, :, 2]
    hlsImg[:, :, 2][hlsImg[:, :, 2] > 1] = 1
    # _, hlsImg[:, :, 2] = cv2.threshold(hlsImg[:, :, 2], 1, 1, cv2.THRESH_TRUNC)
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_HLS2RGB)
    hlsImg = hlsImg * 255
    image = hlsImg.astype(np.uint8)
    
    image = cv2.medianBlur(image, 5)
    image = cv2.GaussianBlur(image, (3,3), 1)
    return image


def load_and_process(img_name):
    image = cv2.imread(img_name)
    # image = process(image)
    image = cv2.resize(image, (image_size, image_size))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def get_label(img_name):
    # # read from file path
    # label = [class_index[os.path.basename(os.path.dirname(img_name))]]

    # read from txt
    txt_name = os.path.splitext(img_name)[0] + '.txt'
    label = set()
    with open(txt_name, 'r') as f:
        for line in f.readlines():
            tokens = line.strip().split()
            label.add(int(tokens[0]))
    label = list(label)

    return label


class Categorizer:
    def __init__(self):
        if multi_label:
            self.worker = MultiLabelBinarizer()
            l = np.arange(num_classes)
            l = l.reshape(num_classes, 1)
            self.worker.fit(l)
    
    def run(self, y):
        if multi_label:
            y = self.worker.transform(y)
        else:
            y = y.reshape(-1, 1)
            y = to_categorical(y, num_classes=num_classes)
        return y


def get_files(data_path):
    files = []
    if os.path.isdir(data_path):
        files = scan_files(data_path, postfix='.jpg')
    elif os.path.isfile(data_path):
        with open(data_path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                files.append(line)
    return files


def allocator(o_queue):
    files = get_files(data_path)
    N_batches = len(files) // batch_size  # truncate data to complete batches
    print("# files:", len(files), "# batches:", N_batches)
    for i in range(N_batches):
        batch = files[i*batch_size : (i+1)*batch_size]
        o_queue.put((batch, N_batches))

        
def dataloader(i_queue, o_queue):   
    categorizer = Categorizer()
    while True:
        item = i_queue.get()
        img_names, N_batches = item
        X, y = [], []
        for img_name in img_names:
            image = load_and_process(img_name)
            label = get_label(img_name)
            X.append(image)
            y.append(label)
        X = np.asarray(X)
        y = np.asarray(y)
        y = categorizer.run(y)
        o_queue.put((X, y, N_batches))
        del X, y


def collector(i_queue):
    if not append and os.path.isfile(save_file):
        os.remove(save_file)
        
    with h5py.File(save_file, 'a') as f:
        if append:
            i = f[i_key]
            l = f[l_key]
        else:
            i = f.create_dataset(i_key, 
                                 shape=(0, image_size, image_size, n_channels), 
                                 dtype='f', 
                                 chunks=(batch_size, image_size, image_size, n_channels),
                                 maxshape=(None, image_size, image_size, n_channels))
            l = f.create_dataset(l_key, 
                                 shape=(0, num_classes), 
                                 dtype='i', 
                                 chunks=(batch_size, num_classes),
                                 maxshape=(None, num_classes))   
            
        batch_count = 0
        while True:
            item = i_queue.get()
            
            X, y, N_batches = item
            batch_count += 1

            i.resize(i.shape[0]+batch_size, axis=0)
            i[-batch_size:] = X
            l.resize(l.shape[0]+batch_size, axis=0)
            l[-batch_size:] = y
            del X, y
            X, y = [], []
                
            if batch_count % 200 == 0:
                print(datetime.now(), "  -->  ", "# of batches collected: ", batch_count)
            if batch_count == N_batches:
                break
    print(datetime.now(), "  -->  ", "finished creating file: ", save_file)
                  
                    
def start_processes(all_processes):
    for ps in all_processes:
        for p in ps:
            p.start()


def join_processes(all_processes):
    for ps in all_processes:
        for p in ps:
            p.join()
                    
                    
q_names = Queue(maxsize=1024)
q_images = Queue(maxsize=1024)

p_allocators = []
p_dataloaders = []
p_collectors = []

p_allocators.append(Process(target=allocator, args=(q_names,)))
for i in range(num_workers):
    p_dataloaders.append(Process(target=dataloader, args=(q_names, q_images)))
p_collectors.append(Process(target=collector, args=(q_images,)))

pps = [p_allocators, p_dataloaders, p_collectors]
start_processes(pps)
join_processes(pps)
