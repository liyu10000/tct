import os
import cv2
import numpy as np
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed


HLS_L = [0.9]
HLS_S = [0.4, 0.5]


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


def hls_trans_smart(image_name, save_path, HLS_L=HLS_L, HLS_S=HLS_S):
    image = cv2.imread(image_name)
    # image = np.asarray(image)

    # 图像归一化，且转换为浮点型
    hlsImg = image.astype(np.float32)
    # hlsImg = hlsImg / 255.0
    hlsImg = cv2.addWeighted(hlsImg, 1./255, hlsImg, 0.0, 0.0)
    
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
    # hlsImg = hlsImg * 255
    hlsImg = cv2.addWeighted(hlsImg, 255, hlsImg, 0, 0)
    image = hlsImg.astype(np.uint8)
    
    image_name_new = os.path.join(save_path, os.path.basename(image_name))
    cv2.imwrite(image_name_new, image)


def batch_change_hls(image_names, save_path):
    for image_name in image_names:
        hls_trans_smart(image_name, save_path)
        
        
def process(data_path, save_path):
    image_names = scan_files(data_path, postfix=".bmp")
    print("# images", len(image_names))
    
    os.makedirs(save_path, exist_ok=True)
    
    executor = ProcessPoolExecutor(max_workers=8)
    tasks = []
    
    batch_size = 10000
    for i in range(0, len(image_names), batch_size):
        batch = image_names[i : i+batch_size]
        tasks.append(executor.submit(batch_change_hls, batch, save_path))

    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))
        
        
if __name__ == "__main__":
    data_path = "/home/ssd_array/data/batch6.4_1216/original"
    save_path = "/home/ssd_array/data/batch6.4_1216/hls09"

    process(data_path, save_path)