import os
import re
import cv2
import random
import numpy as np

from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed



# 11 classes
classes = {"ACTINO":9, "CC":8, "VIRUS":10, "FUNGI":6, "TRI":7, 
           "AGC_A":4, "AGC_B":4, "EC":5, "HSIL_B":2, "HSIL_M":2, 
           "HSIL_S":2, "SCC_G":3, "ASCUS":0, "LSIL_F":0,
           "LSIL_E":1, "SCC_R":3}

# normal background file path
normal_path = ""


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


def get_abn_bk(normal_path):
    normal_files = scan_files(normal_path, postfix=".bmp")
    assert len(normal_files) >= 1
    normal_randf = random.sample(normal_files, 1)
    return cv2.imread(normal_randf)


def put_cell(cell_path, save_path, size=608, background="white"):
    img = cv2.imread(cell_path)

    # half-size image
    img = cv2.pyrDown(img)
    # get image size
    h, w, _ = img.shape

    # get cell size
    p = re.compile("w\d+_h\d+_dx\d+_dy\d+")
    m = p.search(cell_path)
    if not m:
        print("incorrect name format", cell_path)
        return
    cell_w, cell_h, dx, dy = re.findall(r"\d+", m.group())
    cell_w, cell_h = int(cell_w), int(cell_h)
    dx, dy = int(dx), int(dy)

    
    # get sizexsize background
    if background == "white":
        background = np.ones((size, size, 3)) * 255
    elif background == "black":
        background = np.zeros((size, size, 3))
    else:  # use normal cells as background
        background = get_abn_bk()

    # get random position of image and put on background
    if w < size and h < size:
        rand_x = random.randint(0, size-w)
        rand_y = random.randint(0, size-h)
        background[rand_y:rand_y+h, rand_x:rand_x+w, :] = img
    elif w < size:
        rand_x = random.randint(0, size-w)
        rand_y = (size - h) // 2  # non positive value
        background[:, rand_x:rand_x+w, :] = img[-rand_y:size-rand_y, :, :]
    elif h < size:
        rand_x = (size - w) // 2  # non positive value
        rand_y = random.randint(0, size-h)
        background[rand_y:rand_y+h, :, :] = img[:, -rand_x:size-rand_x, :]
    else:
        rand_x = (size - w) // 2  # non positive value
        rand_y = (size - h) // 2  # non positive value
        background[:, :, :] = img[-rand_y:size-rand_y, -rand_x:size-rand_x, :]

    # save image
    pre, pos = os.path.splitext(cell_path)
    basename = os.path.basename(pre)
    pre_new = os.path.join(save_path, basename + "_rx{}_ry{}".format(rand_x, rand_y))
    cell_path_new = pre_new + pos
    cv2.imwrite(cell_path_new, background)

    # save txt for yolo
    txt_path = pre_new + ".txt"
    yolo_x = (rand_x + dx/2 + cell_w/4) / size  # need to half dx/dy/cell_w/cell_h since image is halfed
    yolo_y = (rand_y + dy/2 + cell_h/4) / size
    yolo_w = min(cell_w/2, size) / size
    yolo_h = min(cell_h/2, size) / size
    class_i = classes[os.path.basename(os.path.dirname(cell_path))]
    with open(txt_path, 'w') as f:
        f.write(' '.join([str(a) for a in [class_i, yolo_x, yolo_y, yolo_w, yolo_h]]) + '\n')


def batch_put_cell(cell_paths, save_path):
    for cell_path in cell_paths:
        put_cell(cell_path, save_path, background="white")
        put_cell(cell_path, save_path, background="black")
        put_cell(cell_path, save_path, background="normal")


def put_cells(cell_dir, save_path, postfix=".bmp"):
    os.makedirs(save_path, exist_ok=True)

    files = scan_files(cell_dir, postfix=postfix)
    print("# files:", len(files))

    executor = ProcessPoolExecutor(max_workers=cpu_count())
    tasks = []

    batch_size = 100
    for i in range(0, len(files), batch_size):
        batch = files[i : i+batch_size]
        tasks.append(executor.submit(batch_put_cell, batch, save_path))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))



if __name__ == "__main__":
    cell_dir = "/home/data_samba/Code_by_yuli/batch6.1_cells_b"
    save_path = "/home/data_samba/Code_by_yuli/batch6.1_cells_b_half_in_608"

    put_cells(cell_dir, save_path)