import os
import cv2
import random
import shutil
import numpy as np
from PIL import Image
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed


global HLS_L
global HLS_S

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


def hls_trans_smart(image):
    # image = cv2.imread(image_name)
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
    
    return image


# half the image size and pad/crop to size 299
def half_and_pad_image(image_name, save_dir, depth, size, hls):
    tokens = image_name.rsplit(os.sep, depth+1)
    image_name_ = os.path.join(save_dir, *tokens[1:])
    os.makedirs(os.path.dirname(image_name_), exist_ok=True)
        
    image = cv2.imread(image_name)
    image = cv2.pyrDown(image)
    
    # change l and s of image
    if hls:
        image = hls_trans_smart(image)

#     new_image = np.ones((size, size, 3)) * 255  # white
    new_image = np.zeros((size, size, 3))  # black
    h, w, _ = image.shape
    if h < size and w < size:
        new_image[(size-h)//2:h+(size-h)//2, (size-w)//2:w+(size-w)//2, :] = image
    elif h < size:
        new_image[(size-h)//2:h+(size-h)//2, :, :] = image[:, (w-size)//2:size+(w-size)//2, :]
    elif w < size:
        new_image[:, (size-w)//2:w+(size-w)//2, :] = image[(h-size)//2:size+(h-size)//2, :, :]
    else:
        new_image[:, :, :] = image[(h-size)//2:size+(h-size)//2, (w-size)//2:size+(w-size)//2, :]
#     cv2.imwrite(image_name_, new_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    cv2.imwrite(image_name_, new_image)
        

def batch_half_image(image_names, save_dir, depth, size, hls):
    for image_name in image_names:
        half_and_pad_image(image_name, save_dir, depth, size, hls)
        

def process_half_image(cells_dir, cells_dir_half, depth=1, size=299, hls=True):
    image_names = scan_files(cells_dir, postfix=".bmp")
    print("# images", len(image_names))
    
    executor = ProcessPoolExecutor(max_workers=4)
    tasks = []
    
    batch_size = 1000
    for i in range(0, len(image_names), batch_size):
        batch = image_names[i : i+batch_size]
        tasks.append(executor.submit(batch_half_image, batch, cells_dir_half, depth, size, hls))

    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))
        
        
def split_train_and_valid(data_path, save_path, split=0.1):
    def create_directory(save_path, subdirs):
        for datadir in ["train", "valid"]:
            for subdir in subdirs:
                os.makedirs(os.path.join(save_path, datadir, subdir), exist_ok=True)
    
    def remove_directory(data_path, subdirs):
        for subdir in subdirs:
            shutil.rmtree(os.path.join(data_path, subdir))
    
    subdirs = os.listdir(data_path)
    create_directory(save_path, subdirs)
    
    for subdir in subdirs:
        sub_path = os.path.join(data_path, subdir)
        sub_files = [os.path.join(sub_path, f) for f in os.listdir(sub_path) if f.endswith(".bmp")]
        random.shuffle(sub_files)
        random.shuffle(sub_files)
        random.shuffle(sub_files)
        
        sub_train_path = os.path.join(save_path, "train", subdir)      
        sub_train_files = sub_files[int(len(sub_files)*split):]
        for file in sub_train_files:
            shutil.move(file, sub_train_path)
            
        sub_valid_path = os.path.join(save_path, "valid", subdir)
        sub_valid_files = sub_files[:int(len(sub_files)*split)]
        for file in sub_valid_files:
            shutil.move(file, sub_valid_path)
            
        print("{}: split # {} files to train, # {} files to valid".format(subdir, len(sub_train_files), len(sub_valid_files)))
        
    remove_directory(data_path, subdirs)
    
    
def map_name(file_dir):
    files = scan_files(file_dir, postfix=".bmp")
    name_map = {os.path.splitext(os.path.basename(file))[0]:file for file in files}
    return name_map

def create_directory(save_path, subdirs):
    for datadir in ["train", "valid"]:
        for subdir in subdirs:
            os.makedirs(os.path.join(save_path, datadir, subdir), exist_ok=True)

def remove_directory(data_path, subdirs):
    for subdir in subdirs:
        shutil.rmtree(os.path.join(data_path, subdir))

def get_inter_tokens(file_dir, file_path):
    tokens_dir = os.path.abspath(file_dir).split(os.sep)
    tokens_file = os.path.abspath(os.path.dirname(file_path)).split(os.sep)
    return tokens_file[len(tokens_dir):]

def arrange_by_template(temp_dir, file_dir):
    subdirs = os.listdir(file_dir)
    
    temp_name_map = map_name(temp_dir)
    file_name_map = map_name(file_dir)
    
    for basename in file_name_map:
        if not basename in temp_name_map:
            print(basename + " not found in " + temp_dir)
            continue
        tokens = get_inter_tokens(temp_dir, temp_name_map[basename])
        target_dir = os.path.join(file_dir, *tokens)
        os.makedirs(target_dir, exist_ok=True)
        shutil.move(file_name_map[basename], target_dir)
        
    remove_directory(file_dir, subdirs)
    
    
def rotate(image_name):
    basename = os.path.splitext(image_name)[0]
    jpg = Image.open(image_name)
    jpg.rotate(90).save(basename + "_r90.bmp")
    jpg.rotate(180).save(basename + "_r180.bmp")
    jpg.rotate(270).save(basename + "_r270.bmp")
    jpg.close()
    
def batch_rotate(image_names):
    for image_name in image_names:
        rotate(image_name)
        
def process_rotate(cells_dir):
    image_names = scan_files(cells_dir, postfix=".bmp")
    print("# images", len(image_names))
    
    executor = ProcessPoolExecutor(max_workers=4)
    tasks = []
    
    batch_size = 1000
    for i in range(0, len(image_names), batch_size):
        batch = image_names[i : i+batch_size]
        tasks.append(executor.submit(batch_rotate, batch))

    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))
        
        
def get_inter_tokens(file_dir, file_path):
    tokens_dir = os.path.abspath(file_dir).split(os.sep)
    tokens_file = os.path.abspath(os.path.dirname(file_path)).split(os.sep)
    return tokens_file[len(tokens_dir):]

def copy_and_addon(src_folder, dst_folder, addon, postfix):
    src_files = scan_files(src_folder, postfix=postfix)
    for file in src_files:
        tokens = get_inter_tokens(src_folder, file)
        basename = os.path.splitext(os.path.basename(file))[0] + addon + postfix
        shutil.copy(file, os.path.join(dst_folder, *tokens, basename))
    
def move_and_addon(src_folder, dst_folder, addon, postfix):
    src_files = scan_files(src_folder, postfix=postfix)
    for i,file in enumerate(src_files):
        if i % 10000 == 0:
            print("# files merged", i)
        tokens = get_inter_tokens(src_folder, file)
        basename = os.path.splitext(os.path.basename(file))[0] + addon + postfix
        shutil.move(file, os.path.join(dst_folder, *tokens, basename))
        
        
if __name__ == "__main__":
    cells_dir = "/home/nvme0/liyu/batch6.4-cells/CELLS-0318"
    
    # process original images
    cells_dir_half = "/home/nvme0/liyu/batch6.4-cells/CELLS-half"
    
    process_half_image(cells_dir, cells_dir_half, depth=1, size=299, hls=False)
    split_train_and_valid(cells_dir_half, cells_dir_half)
    process_rotate(os.path.join(cells_dir_half, "train"))
    
    # process original images with HLS_L=0.5
    cells_dir_half_hls05 = "/home/nvme0/liyu/batch6.4-cells/CELLS-half-hls05"
    
    HLS_L = [0.5]
    HLS_S = [0.4, 0.5]
    
    process_half_image(cells_dir, cells_dir_half_hls05, depth=1, size=299, hls=True)
    arrange_by_template(cells_dir_half, cells_dir_half_hls05)
    process_rotate(os.path.join(cells_dir_half_hls05, "train"))
    move_and_addon(cells_dir_half_hls05, cells_dir_half, "_hls05", ".bmp")
    
    # process original images with HLS_L=0.7
    cells_dir_half_hls07 = "/home/nvme0/liyu/batch6.4-cells/CELLS-half-hls07"
    
    HLS_L = [0.7]
    HLS_S = [0.4, 0.5]
    
    process_half_image(cells_dir, cells_dir_half_hls07, depth=1, size=299, hls=True)
    arrange_by_template(cells_dir_half, cells_dir_half_hls07)
    process_rotate(os.path.join(cells_dir_half_hls07, "train"))
    move_and_addon(cells_dir_half_hls07, cells_dir_half, "_hls07", ".bmp")
    
