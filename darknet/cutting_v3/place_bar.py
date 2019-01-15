import os
import cv2
import shutil
import numpy as np
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed


classes_to_place_bar = [2]


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


def read_labels(txt_name, size=608):
    boxes = []
    need_bar = False
    with open(txt_name, 'r') as f:
        for line in f.readlines():
            tokens = line.strip().split()
            labeli = int(tokens[0])
            if labeli in classes_to_place_bar:
                need_bar = True
            cx, cy = size*float(tokens[1]), size*float(tokens[2])
            w, h = size*float(tokens[3]), size*float(tokens[4])
            x_min, y_min = int(cx - w / 2), int(cy - h / 2)
            x_max, y_max = int(cx + w / 2), int(cy + h / 2)
            boxes.append([x_min, y_min, x_max, y_max])
    return boxes if need_bar else []


def find_bar(boxes, size=608, bar_size=200):
    if len(boxes) == 0:
        return -1

    d1, d2, d3, d4 = [], [], [], []
    for box in boxes:
        d1.append(size - bar_size - box[3])
        d2.append(size - bar_size - box[2])
        d3.append(box[1] - bar_size)
        d4.append(box[0] - bar_size)
    distance = [min(d1), min(d2), min(d3), min(d4)]
    bar_i = distance.index(max(distance))

    # print(distance)

    return bar_i if distance[bar_i] > 0 else -1


def place_bar(img_name, save_path, size=608, bar_size=200):
    txt_name = os.path.splitext(img_name)[0] + ".txt"
    boxes = read_labels(txt_name)
    bar_i = find_bar(boxes)

    img = cv2.imread(img_name)
    if bar_i == 0:
        img[size-bar_size:, :, :] = 255
    elif bar_i == 1:
        img[:, size-bar_size:, :] = 255
    elif bar_i == 2:
        img[:bar_size, :, :] = 255
    elif bar_i == 3:
        img[:, :bar_size, :] = 255
    # else:
    #     return

    img_name_new = os.path.join(save_path, os.path.basename(img_name))
    os.makedirs(os.path.dirname(img_name_new), exist_ok=True)
    cv2.imwrite(img_name_new, img)

    
def batch_place_bar(img_names, dst_path):
    for img_name in img_names:
        place_bar(img_name, dst_path)
    

def main(src_path, postfix, dst_path):
    files = scan_files(src_path, postfix=postfix)
    print("# files", len(files))

    executor = ProcessPoolExecutor(max_workers=cpu_count())
    tasks = []

    batch_size = 1000
    for i in range(0, len(files), batch_size):
        batch = files[i : i+batch_size]
        tasks.append(executor.submit(batch_place_bar, batch, dst_path))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))


if __name__ == "__main__":
    src_path = "/home/hdd_array0/batch6_1216/VOC2012/images-HSIL"
    dst_path = "/home/hdd_array0/batch6_1216/VOC2012/images-HSIL-bar"
    postfix = ".bmp"

    main(src_path, postfix, dst_path)
