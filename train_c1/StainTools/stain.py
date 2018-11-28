from __future__ import division

from staintools import ReinhardNormalizer
from staintools import MacenkoNormalizer
from staintools import VahadaneNormalizer

from staintools import standardize_brightness
from staintools.utils.visual import read_image, show, show_colors, build_stack, patch_grid

import os
import cv2
import time
from multiprocessing import cpu_count, Process


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


def main(input_dir, output_dir, depth):
    images_in = scan_files(input_dir, postfix=".jpg")
    print("total of {} images to process".format(len(images_in)))
    
    batch_size = 10
    for i in range(0, len(images_in), batch_size):
        batch = images_in[i : i+batch_size]
#         batch_process_image(images_in=batch, save_dir=output_dir, depth=depth)
        p = Process(target=batch_process_image, args=(batch, output_dir, depth))
        p.start()
        p.join()
        print("added process {} - {}".format(i, i+batch_size))


if __name__ == "__main__":
	input_dir = "/home/nvme/ext_299"
	output_dir = "/home/nvme/ext_299_stained"
	depth = 1

	main(input_dir, output_dir, depth)