import os
import cv2
import shutil

from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed


classes = {0:"AGC", 1:"HSIL-SCC_G", 2:"SCC_R", 3:"EC", 4:"ASCUS", 5:"LSIL", 6:"CC", 
            7:"VIRUS", 8:"FUNGI", 9:"ACTINO", 10:"TRI", 11:"PH", 12:"SC"}


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


def read_label(txt_name):
    labels = []
    with open(txt_name, 'r') as f:
        for line in f.readlines():
            tokens = line.strip().split()
            label = classes[int(tokens[0])]
            labels.append(label)
    if not labels:
        print("empty txt", txt_name)
        return ""
    label = labels[0]
    if len(labels) == labels.count(label):
        return label
    return ""


def resize(img_name, size, save_path, label):
    img = cv2.imread(img_name)
    img = cv2.resize(img, (size, size))
    img_name_new = os.path.join(save_path, label, os.path.basename(img_name))
    cv2.imwrite(img_name_new, img)
    
    
def process(img_name, size, save_path):
    txt_name = os.path.splitext(img_name)[0] + ".txt"
    label = read_label(txt_name)
    if label == "":
        return
    
    resize(img_name, size, save_path, label)
    
    
def batch_process(img_names, size, save_path):
    for img_name in img_names:
        process(img_name, size, save_path)
        

def makedirs(save_path):
    for key,value in classes.items():
        save_path_i = os.path.join(save_path, value)
        os.makedirs(save_path_i, exist_ok=True)

        
def main(data_path, save_path, size=299):
    files = scan_files(data_path, postfix=".bmp")
    print("# files:", len(files))
    
    makedirs(save_path)

    executor = ProcessPoolExecutor(max_workers=4)
    tasks = []

    batch_size = 10000
    for i in range(0, len(files), batch_size):
        batch = files[i : i+batch_size]
        tasks.append(executor.submit(batch_process, batch, size, save_path))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))
        
        
if __name__ == "__main__":
    data_path = "/home/nvme0/liyu/batch6.4/original"
    save_path = "/home/hdd0/Develop/liyu/batch6.4-608-to-299/original"
    main(data_path, save_path)