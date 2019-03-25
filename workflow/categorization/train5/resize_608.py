import os
import cv2
import shutil
import numpy as np

from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed


# # 13 classes
# classes = {0:"AGC", 1:"HSIL-SCC_G", 2:"SCC_R", 3:"EC", 4:"ASCUS", 5:"LSIL", 6:"CC", 
#             7:"VIRUS", 8:"FUNGI", 9:"ACTINO", 10:"TRI", 11:"PH", 12:"SC"}

# 4 classes
classes = {0:'MC', 1:'SC', 2:'RC', 3:'GEC'}


def hls_trans_smart(image, HLS_L=[0.9], HLS_S=[0.4, 0.5]):
    # image = cv2.imread(image_name)
    # image = np.asarray(image)

    # 图像归一化，且转换为浮点型
    hlsImg = image.astype(np.float32)
    hlsImg = hlsImg / 255.0
    # 颜色空间转换 BGR转为HLS
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_BGR2HLS)
    
    # 1.调整亮度
    l = np.average(hlsImg[:,:,1])
    i = len(HLS_L) - 1
    while i != -1 and HLS_L[i] > l:
        i -= 1
    if i != len(HLS_L)-1:
        hls_l = HLS_L[i+1]
        hlsImg[:, :, 1] = hls_l / l * hlsImg[:, :, 1]
        hlsImg[:, :, 1][hlsImg[:, :, 1] > 1] = 1
        # print(image_name, "changing l", l, "to", hls_l)
        
    # 2.调整饱和度
    s = np.average(hlsImg[:,:,2])
    i = len(HLS_S) - 1
    while i != -1 and HLS_S[i] > s:
        i -= 1
    if i != len(HLS_S)-1:
        hls_s = HLS_S[i+1]
        hlsImg[:, :, 2] = hls_s / s * hlsImg[:, :, 2]
        hlsImg[:, :, 2][hlsImg[:, :, 2] > 1] = 1
        # print(image_name, "changing s", s, "to", hls_s)
        
    # HLS2BGR
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_HLS2BGR)
    # 转换为8位unsigned char
    hlsImg = hlsImg * 255
    image = hlsImg.astype(np.uint8)
    
    return image


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
    # img = cv2.imread(img_name)
    # img = cv2.resize(img, (size, size))
    # img_name_new = os.path.join(save_path, label, os.path.basename(img_name))
    # cv2.imwrite(img_name_new, img)
    
    img = cv2.imread(img_name)
    
    img_ori = cv2.resize(img, (size, size))
    img_name_new = os.path.join(save_path, os.path.basename(img_name))
    cv2.imwrite(img_name_new, img_ori)   
    
    img_hls = hls_trans_smart(img)
    pre,pos = os.path.splitext(img_name_new)
    img_name_hls = pre + "_hls09" + pos
    img_hls = cv2.resize(img_hls, (size, size))
    cv2.imwrite(img_name_hls, img_hls) 
    
    
def process(img_name, size, save_path):
    # txt_name = os.path.splitext(img_name)[0] + ".txt"
    # label = read_label(txt_name)
    # if label == "":
    #     return
    
    label = None
    
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
    
    # makedirs(save_path)

    executor = ProcessPoolExecutor(max_workers=4)
    tasks = []

    batch_size = 10000
    for i in range(0, len(files), batch_size):
        batch = files[i : i+batch_size]
        # batch_process(batch, size, save_path)
        tasks.append(executor.submit(batch_process, batch, size, save_path))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))
        
        
if __name__ == "__main__":
    data_path = "/home/hdd0/Develop/liyu/batch6.4/negative"
    save_path = "/home/hdd0/Develop/liyu/batch6.4-608-to-299/negative"
    main(data_path, save_path)