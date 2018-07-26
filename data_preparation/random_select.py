# randomly select part of cropped images from a whole batch
import os
from shutil import copy2, move
from random import shuffle

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

# color = "#aa5500"
# input_path = "F:\\0514-data1-8-size256\\train\\" + color
# output_path = "F:\\0514-data1-8-size256\\val\\" + color
input_path = "F:\\0514-data1-8-size256\\train\\tietu"
output_path = "F:\\0514-data1-8-size256\\val\\tietu-val"
if not os.path.exists(output_path):
    os.makedirs(output_path)
factor = 0.5

image_names = scan_files(input_path)
shuffle(image_names)
for i in range(500):
    copy2(image_names[i], output_path)
    #move(image_names[i], output_path)
