
# coding: utf-8

# In[ ]:


from __future__ import division

from staintools import ReinhardNormalizer
from staintools import MacenkoNormalizer
from staintools import VahadaneNormalizer

from staintools import standardize_brightness
from staintools.utils.visual import read_image, show, show_colors, build_stack, patch_grid

import os
import cv2
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed


# In[ ]:


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


# In[ ]:


def process_image(normalizer, image_in, save_dir, depth):
    tokens = image_in.rsplit(os.sep, depth+1)
    image_out = os.path.join(save_dir, *tokens[1:])
    parent_dir = os.path.dirname(image_out)
    os.makedirs(parent_dir, exist_ok=True)
    r_img = read_image(image_in)
    target = normalizer.transform(r_img)
    target = cv2.cvtColor(target, cv2.COLOR_RGB2BGR)
    cv2.imwrite(image_out, target)
    
def batch_process_image(images_in, save_dir, depth):
    normalizer = VahadaneNormalizer()
    i1 = read_image("./lbp_pic/reference_pic/zs_abnormal.png")
    normalizer.fit(i1)
    
    for image_in in images_in:
        process_image(normalizer, image_in, save_dir, depth)


# In[ ]:


def main(input_dir, output_dir, depth):
    images_in = scan_files(input_dir, postfix=".jpg")
    print("total of {} images to process".format(len(images_in)))
    
    executor = ProcessPoolExecutor(max_workers=cpu_count()-4)
    tasks = []
    
    interval = 100
    for i in range(0, len(images_in), interval):
        batch = images_in[i : i+interval]
#         batch_process_image(images_in=batch, save_dir=output_dir, depth=depth)
        tasks.append(executor.submit(batch_process_image, batch, output_dir, depth))
        print("added {} - {} to process pool".format(i, i+interval))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        job_count -= 1
        print("processed {} images, remaining job count: {}".format(interval, job_count))


# In[ ]:


input_dir = "/home/stimage/Documents/alldata"
output_dir = "/home/stimage/Documents/alldata_stained/"
depth = 1


# In[ ]:


main(input_dir, output_dir, depth)

