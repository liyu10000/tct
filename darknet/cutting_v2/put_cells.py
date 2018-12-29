import os
import re
import cv2
import math
import random
import numpy as np
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed

from utils import scan_files



# 11 yolo classes
yolo_classes = {"ACTINO":9, "CC":8, "VIRUS":10, "FUNGI":6, "TRI":7, "AGC_A":4, 
                "AGC_B":4, "EC":5, "HSIL_B":2, "HSIL_M":2, "HSIL_S":2, "SCC_G":3, 
                "ASCUS":0, "LSIL_F":0, "LSIL_E":1, "SCC_R":3}

# number of times of using each positive cell
pos_cells_num = {"ACTINO":1, "CC":1, "VIRUS":1, "FUNGI":1, "TRI":1, "AGC_A":1, 
                "AGC_B":1, "EC":4, "HSIL_B":1, "HSIL_M":1, "HSIL_S":1, "SCC_G":1, 
                "ASCUS":1, "LSIL_F":1, "LSIL_E":1, "SCC_R":1}


# positive cells path
pos_cells_path = "/home/ssd0/Develop/liyu/train4/train4_posi_cells"

# negative background image path, it should contain sub-folders named by wsi name...
neg_background_path = "/home/ssd0/Develop/liyu/train4/train4_neg_bg/images_v2"

# negative cells image paths, it may have multiple sources
neg_cells_paths = {"path1":"/home/ssd0/Develop/liyu/train4/train4_neg_cells/cells_false_posi/NJ", 
                   "path2":"/home/ssd0/Develop/liyu/train4/train4_neg_cells/cells_false_posi/TC",
                   "path3":"/home/ssd0/Develop/liyu/train4/train4_neg_cells/cells_misleading/NJ", 
                   "path4":"/home/ssd0/Develop/liyu/train4/train4_neg_cells/cells_misleading/TC",
                   "path5":"/home/ssd0/Develop/liyu/train4/train4_neg_cells_from_posi_wsis"}

# negative cells image path, it should contains sub-folders like all/MC/...
neg_cells_path_map = {"ACTINO":[["path1", "ACTINO", 2], ["path2", "ACTINO", 2], ["path3", "ACTINO", 2], ["path4", "ACTINO", 2], ["path5", "all", 8]], 
                      "CC":[["path1", "CC", 2], ["path2", "CC", 2], ["path3", "CC", 2], ["path4", "CC", 2], ["path5", "all", 8]], 
                      "VIRUS":[["path1", "VIRUS", 2], ["path2", "VIRUS", 2], ["path3", "VIRUS", 2], ["path4", "VIRUS", 2], ["path5", "all", 8]], 
                      "FUNGI":[["path1", "FUNGI", 2], ["path2", "FUNGI", 2], ["path3", "FUNGI", 2], ["path4", "FUNGI", 2], ["path5", "all", 8]], 
                      "TRI":[["path1", "TRI", 2], ["path2", "TRI", 2], ["path3", "TRI", 2], ["path4", "TRI", 2], ["path5", "all", 8]], 
                      "AGC_A":[["path1", "AGC_A", 2], ["path2", "AGC_A", 2], ["path3", "AGC_A", 2], ["path4", "AGC_A", 2], ["path5", "all", 8]], 
                      "AGC_B":[["path1", "AGC_B", 2], ["path2", "AGC_B", 2], ["path3", "AGC_B", 2], ["path4", "AGC_B", 2], ["path5", "all", 8]], 
                      "EC":[["path1", "EC", 2], ["path2", "EC", 2], ["path3", "EC", 2], ["path4", "EC", 2], ["path5", "all", 8]], 
                      "HSIL_B":[["path1", "HSIL_B", 2], ["path2", "HSIL_B", 2], ["path3", "HSIL_B", 2], ["path4", "HSIL_B", 2], ["path5", "all", 8]], 
                      "HSIL_M":[["path1", "HSIL_M", 2], ["path2", "HSIL_M", 2], ["path3", "HSIL_M", 2], ["path4", "HSIL_M", 2], ["path5", "all", 8]], 
                      "HSIL_S":[["path1", "HSIL_S", 2], ["path2", "HSIL_S", 2], ["path3", "HSIL_S", 2], ["path4", "HSIL_S", 2], ["path5", "all", 8]], 
                      "SCC_G":[["path1", "SCC_G", 2], ["path2", "SCC_G", 2], ["path3", "SCC_G", 2], ["path4", "SCC_G", 2], ["path5", "all", 8]], 
                      "ASCUS":[["path1", "ASCUS", 2], ["path2", "ASCUS", 2], ["path3", "ASCUS", 2], ["path4", "ASCUS", 2], ["path5", "all", 8]], 
                      "LSIL_F":[["path1", "LSIL_F", 2], ["path2", "LSIL_F", 2], ["path3", "LSIL_F", 2], ["path4", "LSIL_F", 2], ["path5", "all", 8]], 
                      "LSIL_E":[["path1", "LSIL_E", 2], ["path2", "LSIL_E", 2], ["path3", "LSIL_E", 2], ["path4", "LSIL_E", 2], ["path5", "all", 8]], 
                      "SCC_R":[["path1", "SCC_R", 2], ["path2", "SCC_R", 2], ["path3", "SCC_R", 2], ["path4", "SCC_R", 2], ["path5", "all", 8]]}

# number of negative cells used in one image
neg_cells_num = [1, 6]


############### patched images saving path
save_path = "/home/ssd0/Develop/liyu/train4/results608"



def rotate_image(image, degree):
    if degree == 90:
        image = cv2.transpose(image)
        image = cv2.flip(image, flipCode=0)
    elif degree == 180:
        image = cv2.flip(image, flipCode=0)
        image = cv2.flip(image, flipCode=1)
    elif degree == 270:
        image = cv2.transpose(image)
        image = cv2.flip(image, flipCode=1)
    return image


def rotate_coordinates(cell_coordinates, image_size, degree):
    dx, dy, cell_w, cell_h = cell_coordinates
    w, h = image_size

    if degree == 90:
        dx, dy = dy, w - dx - cell_w
        cell_w, cell_h = cell_h, cell_w
    elif degree == 180:
        dx, dy = w - dx - cell_w, h - dy - cell_h
    elif degree == 270:
        dx, dy = h - dy - cell_h, dx
        cell_w, cell_h = cell_h, cell_w

    return dx, dy, cell_w, cell_h


def read_coordinates(txt_name):
    labels_info = []
    with open(txt_name, 'r') as f:
        for line in f.readlines():
            tokens = line.strip().split()
            labels_info.append([tokens[0], float(tokens[1]), float(tokens[2]), float(tokens[3]), float(tokens[4])])
    return labels_info


def get_background(cell_name, useback, size):
    if useback == "white":
        background = np.ones((size, size, 3))
    elif useback == "black":
        background = np.zeros((size, size, 3))
    elif useback == "positive":  # use negative images from positive wsis
        neg_files = []
        for sub_dir in os.listdir(neg_background_path):
            if os.path.basename(cell_name).startswith(sub_dir):
                neg_files = scan_files(os.path.join(neg_background_path, sub_dir), postfix=".bmp")
                break
        if len(neg_files) >= 1:
            neg_randf = random.sample(neg_files, 1)[0]
            background = cv2.imread(neg_randf)
        else:
            background = np.zeros((size, size, 3))
    else:
        background = np.zeros((size, size, 3))
    return background


def py_cpu_nms(dets, thresh):
    x1 = dets[:, 0]
    y1 = dets[:, 1]
    x2 = dets[:, 2]
    y2 = dets[:, 3]
    scores = dets[:, 4]

    #每一个检测框的面积
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    #按照score置信度降序排序
    order = scores.argsort()[::-1]
    # order = [i for i in range(scores.shape[0])]

    keep = [] #保留的结果框集合
    while order.size > 0:
        i = order[0]
        keep.append(i) #保留该类剩余box中得分最高的一个
        #得到相交区域,左上及右下
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        #计算相交的面积,不重叠时面积为0
        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        inter = w * h
        #计算IoU：重叠面积 /（面积1+面积2-重叠面积）
        ovr = inter / (areas[i] + areas[order[1:]] - inter)
        #保留IoU小于阈值的box
        inds = np.where(ovr <= thresh)[0]
        order = order[inds + 1] #因为ovr数组的长度比order数组少一个,所以这里要将所有下标后移一位

    return keep


def put_neg_cells(background, label, size):
    # collect all negative cells for specific label
    neg_cells = []
    sub_paths = neg_cells_path_map[label]
    for sub_path in sub_paths:
        # neg_cells += scan_files(os.path.join(neg_cells_paths[sub_path[0]], sub_path[1]), postfix=".bmp")
        if sub_path[1] == "all":
            sub_neg_cells = scan_files(neg_cells_paths[sub_path[0]], postfix=".bmp")
        else:
            sub_neg_cells = scan_files(os.path.join(neg_cells_paths[sub_path[0]], sub_path[1]), postfix=".bmp")
        neg_cells += random.sample(sub_neg_cells, min(sub_path[2], len(sub_neg_cells)))

    # get number and names of negative cells
    neg_cells_cnt = random.randint(neg_cells_num[0], neg_cells_num[1])
    neg_cells_for_patch = random.sample(neg_cells, min(neg_cells_cnt, len(neg_cells)))
    # print("total", len(neg_cells), "choose", len(neg_cells_for_patch))
    
    # get possible cell positions in background
    neg_cells_possible = []
    dets = []
    for neg_cell in neg_cells_for_patch:
        # tokens = re.findall(r"\d+", neg_cell)  # should follow ..._w123_h234.bmp format
        # neg_w, neg_h = math.ceil(int(tokens[-2])/2), math.ceil(int(tokens[-1])/2)
        neg_img = cv2.imread(neg_cell)
        neg_h, neg_w, _ = neg_img.shape
        neg_x = random.randint(0, size-neg_w)
        neg_y = random.randint(0, size-neg_h)
        neg_cells_possible.append([neg_cell, (neg_x, neg_y, neg_w, neg_h)])
        dets.append([neg_x, neg_y, neg_x+neg_w, neg_y+neg_h, 1])

    # remove overlapping cells
    keep = py_cpu_nms(np.array(dets), thresh=0.1)

    neg_cells_ready = [neg_cells_possible[i] for i in keep]

    # put cells on background
    for neg_cell in neg_cells_ready:
        neg_img = cv2.imread(neg_cell[0])
        # neg_img = cv2.pyrDown(neg_img)
        neg_x, neg_y, neg_w, neg_h = neg_cell[1]
        background[neg_y:neg_y+neg_h, neg_x:neg_x+neg_w, :] = neg_img

    return background


def put_posi_cell(cell_image, cell_coordinates, background, size):
    # get image size
    h, w, _ = cell_image.shape

    # decode cell coordinates in image
    dx, dy, cell_w, cell_h = cell_coordinates

    # get random position of image and put on background
    if w < size and h < size:
        image_x = random.randint(0, size-w)
        image_y = random.randint(0, size-h)
        background[image_y:image_y+h, image_x:image_x+w, :] = cell_image
    elif w < size:
        image_x = random.randint(0, size-w)
        image_y = int((size-cell_h)/2 - dy)  # non positive value
        background[:, image_x:image_x+w, :] = cell_image[-image_y:size-image_y, :, :]
    elif h < size:
        image_x = int((size-cell_w)/2 - dx)  # non positive value
        image_y = random.randint(0, size-h)
        background[image_y:image_y+h, :, :] = cell_image[:, -image_x:size-image_x, :]
    else:
        image_x = int((size-cell_w)/2 - dx)  # non positive value
        image_y = int((size-cell_h)/2 - dy)  # non positive value
        background[:, :, :] = cell_image[-image_y:size-image_y, -image_x:size-image_x, :]

    return background, image_x, image_y


def put_cell(cell_name, save_path, index, useback, rotate=True, size=608):
    # read cell coordinates in image
    txt_name = os.path.splitext(cell_name)[0] + ".txt"
    labels_info = read_coordinates(txt_name)
    label, dx, dy, cell_w, cell_h = labels_info[0]

    # read image
    image = cv2.imread(cell_name)
    h, w, _ = image.shape

    # prepare saving prefix
    pre = os.path.splitext(os.path.basename(cell_name))[0]
    pre_new = os.path.join(save_path, pre)
    
    # put positive and negative cells, with rotation
    degrees = [0, 90, 180, 270] if rotate else [0]
    for degree in degrees:
        # get sizexsize background
        background = get_background(cell_name, useback, size)

        # patch negative cells
        background = put_neg_cells(background, label, size)

        # patch positive cell
        image_rotated = rotate_image(image, degree)
        dx_, dy_, cell_w_, cell_h_ = rotate_coordinates([dx, dy, cell_w, cell_h], [w, h], degree)
        background, image_x, image_y = put_posi_cell(image_rotated, [dx_, dy_, cell_w_, cell_h_], background, size)

        # save image
        cell_name_new = pre_new + "_i{}_r{}.bmp".format(index, degree)
        cv2.imwrite(cell_name_new, background)

        # save txt for yolo
        txt_name_new = pre_new + "_i{}_r{}.txt".format(index, degree)

        yolo_info = []
        for i,label_info in enumerate(labels_info):
            if i > 0:
                dx_, dy_, cell_w_, cell_h_ = rotate_coordinates(label_info[1:], [w, h], degree)
            yolo_x_min = max(image_x + dx_, 0)
            yolo_x_max = min(image_x + dx_ + cell_w_, size)
            yolo_y_min = max(image_y + dy_, 0)
            yolo_y_max = min(image_y + dy_ + cell_h_, size)
            if yolo_x_min > yolo_x_max or yolo_y_min > yolo_y_max:
                continue
            yolo_x = (yolo_x_min + yolo_x_max) / 2 / size
            yolo_y = (yolo_y_min + yolo_y_max) / 2 / size
            yolo_w = (yolo_x_max - yolo_x_min) / size
            yolo_h = (yolo_y_max - yolo_y_min) / size
            # yolo_x = (image_x + dx_ + cell_w_/2) / size
            # yolo_y = (image_y + dy_ + cell_h_/2) / size
            # yolo_w = min(cell_w_, size) / size
            # yolo_h = min(cell_h_, size) / size
            class_i = yolo_classes[label_info[0]]
            yolo_info.append([class_i, yolo_x, yolo_y, yolo_w, yolo_h])

        with open(txt_name_new, 'w') as f:
            for item in yolo_info:
                f.write(' '.join([str(a) for a in item]) + '\n')


def batch_put_cell(cell_names, save_path):
    for cell_name in cell_names:
        label = os.path.basename(os.path.dirname(cell_name))
        for i in range(pos_cells_num[label]):
            # put_cell(cell_name, save_path, index=i, useback="white")
            # put_cell(cell_name, save_path, index=i, useback="black")
            put_cell(cell_name, save_path, index=i, useback="positive")


def put_cells(pos_cells_path, save_path, postfix=".bmp"):
    os.makedirs(save_path, exist_ok=True)

    files = scan_files(pos_cells_path, postfix=postfix)
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

        
# def put_cells(pos_cells_path, save_path, postfix=".bmp"):
#     os.makedirs(save_path, exist_ok=True)

#     files = scan_files(pos_cells_path, postfix=postfix)
#     print("# files:", len(files))

#     for cell_name in files:
#         label = os.path.basename(os.path.dirname(cell_name))
#         for i in range(pos_cells_num[label]):
#             # put_cell(cell_name, save_path, index=i, useback="white")
#             # put_cell(cell_name, save_path, index=i, useback="black")
#             put_cell(cell_name, save_path, index=i, useback="positive")    


if __name__ == "__main__":
    put_cells(pos_cells_path, save_path)


    # # @put_cell
    # cell_name = "/home/hdd0/Develop/tct/darknet/cutting_v2/posi_cells/HSIL_S/2017-09-07-09_24_10_x21529_y26481_w78_h48.bmp"
    # save_path = "./608"
    # put_cell(cell_name, save_path, useback="negative")