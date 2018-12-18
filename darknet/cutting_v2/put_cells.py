import os
import re
import cv2
import random
import numpy as np
from shapely import geometry
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed

from utils import scan_files



# 11 yolo classes
yolo_classes = {"ACTINO":9, "CC":8, "VIRUS":10, "FUNGI":6, "TRI":7, "AGC_A":4, 
                "AGC_B":4, "EC":5, "HSIL_B":2, "HSIL_M":2, "HSIL_S":2, "SCC_G":3, 
                "ASCUS":0, "LSIL_F":0, "LSIL_E":1, "SCC_R":3}

# negative background image path
neg_background_pool = ""

# negative cells image path, it should contains sub-folders like all/MC/...
neg_cells_pool = ""
neg_cells_meta = {"ACTINO":["ACTINO", "all", 10, 50], "CC":["all", 10, 50], "VIRUS":["all", 10, 50], 
                  "FUNGI":["FUNGI", "all", 10, 50], "TRI":["all", 10, 50], "AGC_A":["all", 10, 50], 
                  "AGC_B":["all", 10, 50], "EC":["all", 10, 50], "HSIL_B":["all", 10, 50], 
                  "HSIL_M":["all", 10, 50], "HSIL_S":["MC", "all", 10, 50], "SCC_G":["all", 10, 50], 
                  "ASCUS":["all", 10, 50], "LSIL_F":["all", 10, 50], "LSIL_E":["all", 10, 50], 
                  "SCC_R":["all", 10, 50]}


def is_overlap(label_coords, cell_coords, thres=0.5):
    label_box = geometry.box(label_coords[0], label_coords[1], label_coords[0]+label_coords[2], label_coords[1]+label_coords[3])
    cell_box = geometry.box(cell_coords[0], cell_coords[1], cell_coords[0]+cell_coords[2], cell_coords[1]+cell_coords[3])

    return label_box.intersection(cell_box).area / min(label_box.area, cell_box.area) > thres


def patch_cells(image, label, label_coords, size=608):
    # collect all negative cells for specific label
    neg_cells = []
    for sub_dir in neg_cells_meta[label][:-2]:
        neg_cells += scan_files(os.path.join(neg_cells_pool, sub_dir), postfix=".bmp")

    # get number and names of negative cells
    neg_cells_cnt = random.randint(neg_cells_meta[label][-2], neg_cells_meta[label][-1])
    neg_cells_for_patch = random.sample(neg_cells, neg_cells_cnt)
    
    # get possible cell positions in image
    neg_cells_possible = []
    for neg_cell in neg_cells_for_patch:
        tokens = re.findall(r"\d+", neg_cell)  # should follow ..._w123_h234.bmp format
        neg_w, neg_h = int(tokens[-2]), int(tokens[-1])
        neg_h, neg_w = neg_h//2, neg_w//2  # half the size
        for i in range(5):  # try five times to put in spare spaces
            neg_x = random.randint(0, size-neg_w)
            neg_y = random.randint(0, size-neg_h)
            if not is_overlap(label_coords, (neg_x, neg_y, neg_w, neg_h), thres=0.01):
                neg_cells_possible.append([neg_cell, (neg_x, neg_y, neg_w, neg_h)])
                break

    # remove duplicates
    neg_cells_ready = []
    for neg_cell_p in neg_cells_possible:
        if not neg_cells_ready:
            neg_cells_ready.append(neg_cell_p)
            continue
        for neg_cell_r in neg_cells_ready:
            if not is_overlap(neg_cell_p[1], neg_cell_r[1]):
                neg_cells_ready.append(neg_cell_p)

    # put cells on image
    for neg_cell in neg_cells_ready:
        neg_img = cv2.imread(neg_cell[0])
        neg_img = cv2.pyrDown(neg_img)
        neg_h, neg_w, _ = neg_img.shape
        neg_x, neg_y = neg_cell[1][0], neg_cell[1][1]
        image[neg_y:neg_y+neg_h, neg_x:neg_x+neg_w, :] = neg_img

    return image


def get_neg_bk(neg_background_pool):
    neg_files = scan_files(neg_background_pool, postfix=".bmp")
    assert len(neg_files) >= 1
    neg_randf = random.sample(neg_files, 1)[0]
    return cv2.imread(neg_randf)


def put_cell(cell_name, save_path, size=608, background="white"):
    image = cv2.imread(cell_name)

    # half-size image
    image = cv2.pyrDown(image)
    # get image size
    h, w, _ = image.shape

    # get cell size
    p = re.compile("w\d+_h\d+_dx\d+_dy\d+")
    m = p.search(cell_name)
    if not m:
        print("incorrect name format", cell_name)
        return
    cell_w, cell_h, dx, dy = re.findall(r"\d+", m.group())
    # need to half dx/dy/cell_w/cell_h since image is halfed
    cell_w, cell_h = int(cell_w)/2, int(cell_h)/2
    dx, dy = int(dx)/2, int(dy)/2

    
    # get sizexsize background
    if background == "white":
        background = np.ones((size, size, 3)) * 255
    elif background == "black":
        background = np.zeros((size, size, 3))
    else:  # use negative cells as background
        background = get_neg_bk()

    # get random position of image and put on background
    if w < size and h < size:
        image_x = random.randint(0, size-w)
        image_y = random.randint(0, size-h)
        background[image_y:image_y+h, image_x:image_x+w, :] = image
    elif w < size:
        image_x = random.randint(0, size-w)
        image_y = int((size-cell_h)/2 - dy)  # non positive value
        background[:, image_x:image_x+w, :] = image[-image_y:size-image_y, :, :]
    elif h < size:
        image_x = int((size-cell_w)/2 - dx)  # non positive value
        image_y = random.randint(0, size-h)
        background[image_y:image_y+h, :, :] = image[:, -image_x:size-image_x, :]
    else:
        image_x = int((size-cell_w)/2 - dx)  # non positive value
        image_y = int((size-cell_h)/2 - dy)  # non positive value
        background[:, :, :] = image[-image_y:size-image_y, -image_x:size-image_x, :]

    # patch negative cells
    label = os.path.basename(os.path.dirname(cell_name))
    # background = patch_cells(background, label, (image_x + dx, image_y + dy, min(cell_w, size), min(cell_h, size)))

    # save image
    pre, pos = os.path.splitext(cell_name)
    basename = os.path.basename(pre)
    pre_new = os.path.join(save_path, basename + "_rx{}_ry{}".format(image_x, image_y))
    cell_name_new = pre_new + pos
    cv2.imwrite(cell_name_new, background)

    # save txt for yolo
    txt_path = pre_new + ".txt"
    yolo_x = (image_x + dx + cell_w/2) / size
    yolo_y = (image_y + dy + cell_h/2) / size
    yolo_w = min(cell_w, size) / size
    yolo_h = min(cell_h, size) / size
    class_i = yolo_classes[label]
    with open(txt_path, 'w') as f:
        f.write(' '.join([str(a) for a in [class_i, yolo_x, yolo_y, yolo_w, yolo_h]]) + '\n')


def batch_put_cell(cell_names, save_path):
    for cell_name in cell_names:
        # put_cell(cell_name, save_path, background="white")
        put_cell(cell_name, save_path, background="black")
        # put_cell(cell_name, save_path, background="negative")


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