# coding=utf-8
import os
import cv2
import random
import numpy as np
import openslide
import xml.dom.minidom
from PIL import Image
from datetime import datetime
from shapely import geometry
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed

from tslide.tslide import TSlide
from utils import generate_name_path_dict


# all positive cells
all_posi_cells = {"ACTINO", "CC", "VIRUS", "FUNGI", "TRI", "AGC_A", "AGC_B", "EC", "HSIL_B", 
                  "HSIL_M", "HSIL_S", "SCC_G", "ASCUS", "LSIL_F", "LSIL_E", "SCC_R"}


# the scale of background relative to cell box
scales = {"ACTINO":[2.0, 4.0], 
          "CC":[2.0, 4.0], 
          "VIRUS":[2.0, 4.0], 
          "FUNGI":[2.0, 4.0], 
          "TRI":[3.0, 5.0], 
          "AGC_A":[2.0, 4.0], 
          "AGC_B":[2.0, 4.0], 
          "EC":[2.0, 4.0], 
          "HSIL_B":[2.0, 3.0], 
          "HSIL_M":[2.0, 3.0], 
          "HSIL_S":[2.0, 4.0], 
          "SCC_G":[2.0, 4.0], 
          "ASCUS":[2.0, 4.0], 
          "LSIL_F":[2.0, 4.0], 
          "LSIL_E":[2.0, 4.0], 
          "SCC_R":[2.0, 4.0], 
          "MC":[1.2, 1.5], 
          "SC":[1.2, 1.5], 
          "RC":[1.2, 1.5], 
          "GEC":[1.2, 1.5]}

# when cell size reaches a minimum, use fixed size window, instead of scaling
fix_size = {"VIRUS":{"mini_thres":20, "fix_size":80}, 
            "FUNGI":{"mini_thres":20, "fix_size":80}, 
            "TRI":{"mini_thres":20, "fix_size":80}, 
            "AGC_A":{"mini_thres":20, "fix_size":80}, 
            "AGC_B":{"mini_thres":20, "fix_size":80}, 
            "EC":{"mini_thres":20, "fix_size":80}, 
            "HSIL_B":{"mini_thres":20, "fix_size":80}, 
            "HSIL_M":{"mini_thres":20, "fix_size":80}, 
            "HSIL_S":{"mini_thres":20, "fix_size":80}}


def is_overlap(cell1_coords, cell2_coords, thres=0.5):
    cell1_box = geometry.box(cell1_coords[0], cell1_coords[1], cell1_coords[0]+cell1_coords[2], cell1_coords[1]+cell1_coords[3])
    cell2_box = geometry.box(cell2_coords[0], cell2_coords[1], cell2_coords[0]+cell2_coords[2], cell2_coords[1]+cell2_coords[3])
    return cell1_box.intersection(cell2_box).area / min(cell1_box.area, cell2_box.area) > thres


# get coordinates of labels in a xml
def get_all_labels(xml_file):
    """
        xml_file: single xml file for tif
        return: [{class_i, x_min, y_min, x_max, y_max},]
    """
    DOMTree = xml.dom.minidom.parse(xml_file)
    collection = DOMTree.documentElement
    annotations = collection.getElementsByTagName("Annotation")

    labels = []
    for annotation in annotations:
        coordinates = annotation.getElementsByTagName("Coordinate")
        x_coords = []
        y_coords = []
        for coordinate in coordinates:
            x_coords.append(float(coordinate.getAttribute("X")))
            y_coords.append(float(coordinate.getAttribute("Y")))                    
        x_min, x_max = int(min(x_coords)), int(max(x_coords))
        y_min, y_max = int(min(y_coords)), int(max(y_coords))
        cell = annotation.getElementsByTagName("Cell") # note it's a "list"
        class_i = cell[0].getAttribute("Type")

        if not class_i in all_posi_cells:
            continue

        labels.append({"class_i":class_i, 
                       "x_min":x_min, 
                       "y_min":y_min, 
                       "x_max":x_max, 
                       "y_max":y_max})
    return labels


def adjust_window(win_coords, all_labels):
    x_win, y_win, w_win, h_win = win_coords
    x_min_win, y_min_win = x_win, y_win
    x_max_win, y_max_win = x_win+w_win, y_win+h_win

    add_labels = []
    for label in all_labels:
        x_min, y_min = label["x_min"], label["y_min"]
        x_max, y_max = label["x_max"], label["y_max"]

        vertices = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
        need_shift = False
        for vertex in vertices:
            if x_min_win < vertex[0] < x_max_win and y_min_win < vertex[1] < y_max_win:
                need_shift = True
        if need_shift:
            x_min_win = min(x_min, x_min_win)
            y_min_win = min(y_min, y_min_win)
            x_max_win = max(x_max, x_max_win)
            y_max_win = max(y_max, y_max_win)
            add_labels.append(label.copy())

    return [x_min_win, y_min_win, x_max_win-x_min_win, y_max_win-y_min_win], add_labels


# get coordinates of labels in a xml
def get_labels(xml_file):
    """
        xml_file: single xml file for tif
        return: [{class_i, x_min, y_min, x_max, y_max},]
    """

    # read all labels
    all_labels = get_all_labels(xml_file)

    DOMTree = xml.dom.minidom.parse(xml_file)
    collection = DOMTree.documentElement
    annotations = collection.getElementsByTagName("Annotation")

    labels = []
    for annotation in annotations:
        coordinates = annotation.getElementsByTagName("Coordinate")
        x_coords = []
        y_coords = []
        for coordinate in coordinates:
            x_coords.append(float(coordinate.getAttribute("X")))
            y_coords.append(float(coordinate.getAttribute("Y")))                    
        x_min, x_max = int(min(x_coords)), int(max(x_coords))
        y_min, y_max = int(min(y_coords)), int(max(y_coords))
        x, y = x_min, y_min
        w, h = x_max - x_min, y_max - y_min
        cell = annotation.getElementsByTagName("Cell") # note it's a "list"
        class_i = cell[0].getAttribute("Type")

        if not class_i in scales:
            continue

        # check if a minimum size is defined and the cell reaches the minimum
        if (class_i in fix_size) and (w < fix_size[class_i]["mini_thres"] or h < fix_size[class_i]["mini_thres"]):
            w_win = fix_size[class_i]["fix_size"]
            h_win = fix_size[class_i]["fix_size"]
        else:
            # random window size
            scale = random.uniform(scales[class_i][0], scales[class_i][1])
            w_win = int(w * scale)
            h_win = int(h * scale)


        # adjust window to include additional cells in sight
        win_coords, add_labels = adjust_window([x-(w_win-w)/2, y-(h_win-h)/2, w_win, h_win], all_labels)

        for add_label in add_labels:
            add_label["dx"] = add_label["x_min"] - win_coords[0]
            add_label["dy"] = add_label["y_min"] - win_coords[1]

        # random cell position
        # dx = random.randint(0, w_win-w)
        # dy = random.randint(0, h_win-h)
        # place cell in center
        # dx = int((w_win - w)/2)
        # dy = int((h_win - h)/2)

        labels.append({"class_i":class_i, 
                       "x":x, 
                       "y":y,
                       "x_win":int(win_coords[0]), 
                       "y_win":int(win_coords[1]), 
                       "w_win":int(win_coords[2]), 
                       "h_win":int(win_coords[3]), 
                       "add_labels":add_labels})
    return labels


def cell_sampling(xml_path, tif_path, save_path):
    labels = get_labels(xml_path)

    # return if no cells to cut
    if not labels:
        return

    try:
        try:
            slide = openslide.OpenSlide(tif_path)
        except:
            slide = TSlide(tif_path)
    except:
        print("ERROR: can not open pic ", tif_path)
        exit()

    basename = os.path.splitext(os.path.basename(xml_path))[0]
    for label in labels:
        window = slide.read_region((label["x_win"], label["y_win"]), 0, (label["w_win"], label["h_win"])).convert("RGB")
        window = np.asarray(window)
        window = cv2.cvtColor(window, cv2.COLOR_RGB2BGR)
        window = cv2.pyrDown(window)

        basename_new = "{}_x{}_y{}".format(basename, label["x"], label["y"])

        # save image
        win_path = os.path.join(save_path, label["class_i"], basename_new+".bmp")
        os.makedirs(os.path.dirname(win_path), exist_ok=True)
        cv2.imwrite(win_path, window)

        # save coordinates info
        txt_path = os.path.join(save_path, label["class_i"], basename_new+".txt")
        values = []
        for add_label in label["add_labels"]:
            values.append([add_label["class_i"], 
                           add_label["dx"]/2, 
                           add_label["dy"]/2, 
                           (add_label["x_max"]-add_label["x_min"])/2, 
                           (add_label["y_max"]-add_label["y_min"])/2])
        # values = [label["class_i"], label["dx"]/2, label["dy"]/2, label["w"]/2, label["h"]/2]
        with open(txt_path, 'w') as f:
            for value in values:
                f.write(' '.join([str(a) for a in value]) + '\n')

    slide.close()

    print("finished cutting {}, # cells: {}".format(tif_path, len(labels)))



def cut_cells(xml_dict, tif_dict, save_path):
    executor = ProcessPoolExecutor(max_workers=cpu_count() - 4)
    tasks = []

    for basename in xml_dict:
        xml_path = xml_dict[basename]
        tif_path = tif_dict[basename]
        tasks.append(executor.submit(cell_sampling, xml_path, tif_path, save_path))

    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))            



if __name__ == "__main__":
    # generate name mapping
    xml_files_path = '/home/data_samba/DATA/4TRAIN_DATA/20181216_BATCH_6.1/XMLS_CHECKED'
    tif_files_path = '/home/data_samba/DATA/4TRAIN_DATA/20181102/DATA_FOR_TRAIN/TIFFS'

    xml_dict = generate_name_path_dict(xml_files_path, ['.xml'])
    tif_dict = generate_name_path_dict(tif_files_path, ['.tif', '.kfb'])

    count = 0
    for basename in xml_dict:
        if basename not in tif_dict:
            print("xml does not match with tif", basename)
        else:
            count += 1
    print("number of matched files", count)

    save_path = "/home/data_samba/Code_by_yuli/batch6.1_cells_b"

    cut_cells(xml_dict, tif_dict, save_path)



    # # @test cell_sampling
    # xml_path = "/home/hdd0/Develop/xxx/tif-xml/2017-09-07-09_24_10.xml"
    # tif_path = "/home/hdd0/Develop/xxx/tif-xml/2017-09-07-09_24_10.kfb"
    # save_path = "/home/hdd0/Develop/xxx/cells"

    # cell_sampling(xml_path, tif_path, save_path)