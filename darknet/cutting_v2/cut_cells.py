# coding=utf-8
import os
import cv2
import random
import numpy as np
import openslide
import xml.dom.minidom
from PIL import Image
from datetime import datetime
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed

from tslide.tslide import TSlide
from utils import generate_name_path_dict


# the scale of background relative to cell box
scales = {"ACTINO":[2.0, 4.0], "CC":[2.0, 4.0], "VIRUS":[2.0, 4.0], "FUNGI":[2.0, 4.0], 
          "TRI":[2.0, 4.0], "AGC_A":[1.5, 3.0], "AGC_B":[2.0, 4.0], "EC":[2.0, 4.0], 
          "HSIL_B":[1.5, 3.0], "HSIL_M":[1.5, 3.0], "HSIL_S":[2.0, 3.0], "SCC_G":[2.0, 4.0], 
          "ASCUS":[2.0, 4.0], "LSIL_F":[2.0, 4.0], "LSIL_E":[2.0, 4.0], "SCC_R":[2.0, 4.0], 
          "MC":[1.05, 1.1], "SC":[1.05, 1.1], "RC":[1.05, 1.1], "GEC":[1.05, 1.1]}


# scales = {"LSIL_E":[5.0, 8.0], "LSIL_F":[5.0, 8.0]}



# get coordinates of labels in a xml
def get_labels(xml_file):
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
        x, y = x_min, y_min
        w, h = x_max - x_min, y_max - y_min
        cell = annotation.getElementsByTagName("Cell") # note it's a "list"
        class_i = cell[0].getAttribute("Type")

        if not class_i in scales:
            continue

        # random window size
        scale = random.uniform(scales[class_i][0], scales[class_i][1])
        w_win = int(w * scale)
        h_win = int(h * scale)
        # random cell position
        # dx = random.randint(0, w_win-w)
        # dy = random.randint(0, h_win-h)

        dx = int((w_win - w)/2)
        dy = int((h_win - h)/2)

        labels.append({"class_i":class_i, 
                       "x":x, 
                       "y":y, 
                       "w":w, 
                       "h":h, 
                       "w_win":w_win, 
                       "h_win":h_win, 
                       "x_win":x - dx, 
                       "y_win":y - dy, 
                       "dx":dx, 
                       "dy":dy})
    return labels


def cell_sampling(xml_path, tif_path, save_path):
    labels = get_labels(xml_path)

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

        basename_new = "{}_x{}_y{}_w{}_h{}".format(basename, label["x"], label["y"], label["w"], label["h"])

        # save image
        win_path = os.path.join(save_path, label["class_i"], basename_new+".bmp")
        os.makedirs(os.path.dirname(win_path), exist_ok=True)
        cv2.imwrite(win_path, window)

        # save coordinates info
        txt_path = os.path.join(save_path, label["class_i"], basename_new+".txt")
        values = [label["class_i"], label["dx"]/2, label["dy"]/2, label["w"]/2, label["h"]/2]
        with open(txt_path, 'w') as f:
            f.write(' '.join([str(a) for a in values]) + '\n')

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
    # xml_path = "/home/hdd0/Develop/tct/darknet/cutting_v2/tif-xml/2017-09-07-09_24_10.xml"
    # tif_path = "/home/hdd0/Develop/tct/darknet/cutting_v2/tif-xml/2017-09-07-09_24_10.kfb"
    # save_path = "/home/hdd0/Develop/tct/darknet/cutting_v2/cells"

    # cell_sampling(xml_path, tif_path, save_path)