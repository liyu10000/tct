import os
import cv2
import lmdb
import caffe
import random
import numpy as np
from datetime import datetime
from multiprocessing import Process, Queue, JoinableQueue, Lock, cpu_count



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


def parse_txt(txt_name):
    name_labels = []
    with open(txt_name, 'r') as f:
        for line in f.readlines():
            name, label = line.strip().split()
            label = int(label)
            name_labels.append([name, label])
    return name_labels


def parse_dir(dir_name):
    name_labels = []
    classes = os.listdir(dir_name)
    classes.sort()
    for i,class_i in enumerate(classes):
        names = os.listdir(os.path.join(dir_name, class_i))
        for name in names:
            name = os.path.join(dir_name, class_i, name)
            name_labels.append([name, i])
    return name_labels


def read_image(img_name, size=224):
    img = cv2.imread(img_name)
    img = cv2.resize(img, (size, size))
    img = np.transpose(img, (2, 0, 1)) # hwc to chw
    return img


def image_names_generator(queue_in, queue_out, data_src):
    if os.path.isfile(data_src):
        name_labels = parse_txt(data_src)
    elif os.path.isdir(data_src):
        name_labels = parse_dir(data_src)
    else:
        print("invalid data source.")
        return

    N = len(name_labels)
    print("# total files to add: ", N)
    queue_out.put(N)

    random.shuffle(name_labels)
    random.shuffle(name_labels)
    random.shuffle(name_labels)

    for name_label in name_labels:
        queue_in.put(name_label)


def image_reader(queue_in, queue_out):
    while True:
        name, label = queue_in.get()
        img = read_image(name)
        queue_out.put([img, label])


def lmdb_maker(queue_out, lmdb_name, append=False, size=224):
    # N = len(name_labels)
    N = queue_out.get()
    map_size = N * 3 * size * size * 3  # last 3 for redundancy purposes
    # map_size = 137438953472 # 1 TB, still good for use
    
    env = lmdb.open(lmdb_name, map_size=map_size)
    
    if append:
        max_key = env.stat()["entries"] # assume all str_ids are consecutive and start from 0,1,2,3,...
        
        # reopen env with bigger size
        env.close()
        map_size = (max_key + N) * 3 * size * size * 3
        env = lmdb.open(lmdb_name, map_size=map_size)
        
        print("Existed num of samples: ", max_key)
    else:
        max_key = 0
        print("Create new lmdb.")

    i = 0
    with env.begin(write=True) as txn:
        # txn is a Transaction object
        while i < N:
            img, label = queue_out.get()
            
            datum = caffe.proto.caffe_pb2.Datum()
            datum.channels = 3
            datum.height = size
            datum.width = size
            datum.data = img.tobytes()  # or .tostring() if numpy < 1.9
            datum.label = label
            str_id = '{:08}_{}'.format(i + max_key, name)

            # The encode is only essential in Python 3
            txn.put(str_id.encode('ascii'), datum.SerializeToString())
            
            if i % 1000 == 0:
                print(datetime.now(), " --> ", i)

            i += 1

    print("finished adding data")
        
    
def make_lmdb(data_src, lmdb_name, append=False, size=224):
    if os.path.isfile(data_src):
        name_labels = parse_txt(data_src)
    elif os.path.isdir(data_src):
        name_labels = parse_dir(data_src)
    else:
        print("invalid data source.")
        return
    
    random.shuffle(name_labels)
    random.shuffle(name_labels)
    random.shuffle(name_labels)
    
    N = len(name_labels)
    map_size = N * 3 * size * size * 3  # last 3 for redundancy purposes
    # map_size = 137438953472 # 1 TB, still good for use
    
    env = lmdb.open(lmdb_name, map_size=map_size)
    
    if append:
        max_key = env.stat()["entries"] # assume all str_ids are consecutive and start from 0,1,2,3,...
        # # a more thorough approach
        # max_key = 0
        # for key, value in env.cursor():
        #     max_key = max(max_key, key)
        
        # reopen env with bigger size
        env.close()
        map_size = (max_key + N) * 3 * size * size * 3
        env = lmdb.open(lmdb_name, map_size=map_size)
        
        print("Existed num of samples: ", max_key)
    else:
        max_key = 0
        print("Create new lmdb.")
    
    with env.begin(write=True) as txn:
        # txn is a Transaction object
        for i,name_label in enumerate(name_labels):
            name, label = name_label
            img = read_image(name, size)
            
            datum = caffe.proto.caffe_pb2.Datum()
            datum.channels = 3
            datum.height = size
            datum.width = size
            datum.data = img.tobytes()  # or .tostring() if numpy < 1.9
            datum.label = label
            str_id = '{:08}_{}'.format(i + max_key, name)

            # The encode is only essential in Python 3
            txn.put(str_id.encode('ascii'), datum.SerializeToString())
            
            if i % 1000 == 0:
                print(datetime.now(), " --> ", i)


def get_num_records(lmdb_name):
    env = lmdb.open(lmdb_name)
    max_key = env.stat()["entries"] # assume all str_ids are consecutive and start from 0,1,2,3,...
    env.close()
    return max_key


def delete_from_lmdb(lmdb_name, keys, size=224):
    N = get_num_records(lmdb_name)
    map_size = N * 3 * size * size * 3  # last 3 for redundancy purposes
    env = lmdb.open(lmdb_name, map_size=map_size)
    with env.begin(write=True) as txn:
        for key in keys:
            str_id = '{:08}'.format(key).encode('ascii')
            status = txn.delete(str_id)
            if not status:
                print("Does not exist:", key)



if __name__ == "__main__":
    data_src = "/home/hdd0/Data/batch6.4-cells/CELLS-half/train"
    lmdb_name = "/home/nvme/batch6.4-cells-lmdb/train"
    append = False


#     # @test make_lmdb
#     make_lmdb(data_src, lmdb_name, append=append)


    # @test multiprocessed make_lmdb
    queue_in = Queue(maxsize=10240)
    queue_out = Queue()

    image_names_generators = []
    image_readers = []
    lmdb_makers = []

    # create processes
    image_names_generators.append(Process(target=image_names_generator, args=(queue_in, queue_out, data_src)))
    
    num_workers = 4
    for i in range(num_workers):
        image_readers.append(Process(target=image_reader, args=(queue_in, queue_out), daemon=False))

    lmdb_makers.append(Process(target=lmdb_maker, args=(queue_out, lmdb_name, append), daemon=False))
    # lmdb_maker(queue_out, lmdb_name, append=append)

    # start processes
    for p in image_names_generators:
        p.start()

    for p in image_readers:
        p.start()

    for p in lmdb_makers:
        p.start()

    # synchronize processes
    for p in image_names_generators:
        p.join()

    for p in image_readers:
        p.join()

    for p in lmdb_makers:
        p.join()