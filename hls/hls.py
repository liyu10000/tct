import os
import cv2
import numpy as np
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed


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


def hls_trans(image_name, depth, save_path, HLS_L=0.20, HLS_S=0.8):
    image = cv2.imread(image_name)

    # 图像归一化，且转换为浮点型
    hlsImg = image.astype(np.float32)
    hlsImg = hlsImg / 255.0
    # 颜色空间转换 BGR转为HLS
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_BGR2HLS)
    # 1.调整亮度, 2.将hlsCopy[:, :, 1]和hlsCopy[:, :, 2]中大于1的全部截取
    hlsImg[:, :, 1] = (1.0 + HLS_L) * hlsImg[:, :, 1]
    hlsImg[:, :, 1][hlsImg[:, :, 1] > 1] = 1
    # 2.调整饱和度
    hlsImg[:, :, 2] = (1.0 + HLS_S) * hlsImg[:, :, 2]
    hlsImg[:, :, 2][hlsImg[:, :, 2] > 1] = 1
    # HLS2BGR
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_HLS2BGR)
    # 转换为8位unsigned char
    hlsImg = hlsImg * 255
    image = hlsImg.astype(np.uint8)
    
    tokens = image_name.rsplit(os.sep, depth+1)
    image_name_out = os.path.join(save_path, *tokens[1:])
    os.makedirs(os.path.dirname(image_name_out), exist_ok=True)

    cv2.imwrite(image_name_out, image)


def batch_hls_trans(image_names, depth, save_path, HLS_L=0.20, HLS_S=0.8):
    for image_name in image_names:
        hls_trans(image_name, depth, save_path, HLS_L, HLS_S)


def process(image_path, depth, save_path, HLS_L=0.20, HLS_S=0.8):
    image_names = scan_files(image_path, postfix=".jpg")
    print("total of {} images to process".format(len(image_names)))

    executor = ProcessPoolExecutor(max_workers=cpu_count() - 2)
    tasks = []

    batch_size = 1000
    for i in range(0, len(image_names), batch_size):
        batch = image_names[i : i+batch_size]
        tasks.append(executor.submit(batch_hls_trans, batch, depth, save_path, HLS_L, HLS_S))

    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: {}".format(job_count))



if __name__ == "__main__":
    image_path = "/home/nvme/CELLS"
    save_path = "/home/nvme/CELLS_hls"
    # hls_trans(image_name, 1, save_path)
    process(image_path, 1, save_path)