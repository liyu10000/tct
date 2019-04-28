import os
import cv2
import random
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


def calc_batch(image_names):
    avg = np.zeros((299,299,3))
    for image_name in image_names:
        avg += cv2.imread(image_name)
    avg /= len(image_names)
    return avg


def subt_batch(image_names, avg_img, save_path, depth):
    for image_name in image_names:
        tokens = image_name.rsplit(os.sep, depth+1)
        image_name_ = os.path.join(save_path, *tokens[1:])
        parent_dir = os.path.dirname(image_name_)
        os.makedirs(parent_dir, exist_ok=True)
        
        image = cv2.imread(image_name)
        avg = cv2.imread(avg_img)
        image -= avg  # perhaps wrong, oh, well, exactly.
        cv2.imwrite(image_name_, image)


def calc_mean(data_path):
    image_names = scan_files(data_path, postfix=".bmp")
    print("# files", len(image_names))
    random.shuffle(image_names)
    random.shuffle(image_names)

    executor = ProcessPoolExecutor(max_workers=8)
    tasks = []

    batch_size = 64
    batch_count = len(image_names) // batch_size
    for i in range(batch_count):
        batch = image_names[i * batch_size : (i+1) * batch_size]
        tasks.append(executor.submit(calc_batch, batch))

    avg = np.zeros((299,299,3))
    job_count = len(tasks)
    for future in as_completed(tasks):
        avg += future.result()
        job_count -= 1
        print("One Job Done, Remaining Job Count: {}".format(job_count))
    
    avg /= batch_count
    cv2.imwrite('./average.bmp', avg)
    


if __name__ == "__main__":
    data_path = "/home/ssd_array0/Data/batch6.4_cells/CELLS-half"

    calc_mean(data_path)