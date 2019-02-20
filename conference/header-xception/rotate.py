import os
import cv2
import random
import shutil
import numpy as np
from PIL import Image
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
    
    executor = ProcessPoolExecutor(max_workers=8)
    tasks = []
    
    batch_size = 10000
    for i in range(0, len(image_names), batch_size):
        batch = image_names[i : i+batch_size]
        tasks.append(executor.submit(batch_rotate, batch))

    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))
        
        
if __name__ == "__main__":
    cells_dir = "/home/hdd0/Develop/liyu/batch6.4-608-to-299/negative"
    
    process_rotate(cells_dir)