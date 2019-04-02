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


def hls_trans(image):

    hlsImg = image.astype(np.float32)
    hlsImg = hlsImg / 255.0

    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_BGR2HLS)

    hlsImg[:, :, 2] = 1.5 * hlsImg[:, :, 2]
    hlsImg[:, :, 2][hlsImg[:, :, 2] > 1] = 1

    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_HLS2BGR)

    hlsImg = hlsImg * 255
    image = hlsImg.astype(np.uint8)
    
    return image


def process(image_name, save_path):
    image = cv2.imread(image_name)
    image = hls_trans(image)
    image = cv2.medianBlur(image, 5)
    image = cv2.GaussianBlur(image, (3,3), 1)
    
    basename = os.path.basename(image_name)
    image_name_new = os.path.join(save_path, basename)
    cv2.imwrite(image_name_new, image)


def batch_process(image_names, save_path):
    for image_name in image_names:
        process(image_name, save_path)


def main(data_path, save_path):
    files = scan_files(data_path, postfix=".bmp")
    print("# files", len(files))

    executor = ProcessPoolExecutor(max_workers=8)
    tasks = []

    batch_size = 10000
    for i in range(0, len(files), batch_size):
        batch = files[i : i+batch_size]
#         batch_process(batch, save_path)
        tasks.append(executor.submit(batch_process, batch, save_path))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))


if __name__ == "__main__":
    data_path = "/home/ssd_array0/Data/batch6.4_1216/fungi"
    save_path = "/home/ssd_array0/Data/batch6.4_1216/fungi"

    main(data_path, save_path)


#     data_path = "/home/ssd_array0/Data/batch6.4_1216/rotate"
#     save_path = "/home/ssd_array0/Data/batch6.4_1216/rotate"

#     main(data_path, save_path)


#     data_path = "/home/ssd_array0/Data/batch6.4_1216/rotate-added"
#     save_path = "/home/ssd_array0/Data/batch6.4_1216/rotate-added"

#     main(data_path, save_path)
