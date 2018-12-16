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
scales = {"ACTINO":[1.2, 1.5], "CC":[1.2, 1.5], "VIRUS":[1.2, 1.5], "FUNGI":[1.2, 1.5], "TRI":[1.2, 1.5], 
          "AGC_A":[1.2, 1.5], "AGC_B":[1.2, 1.5], "EC":[1.2, 1.5], "HSIL_B":[1.2, 1.5], "HSIL_M":[1.2, 1.5], 
          "HSIL_S":[1.2, 1.5], "SCC_G":[1.2, 1.5], "ASCUS":[1.2, 1.5], "LSIL_F":[1.2, 1.5],
          "LSIL_E":[1.2, 1.5], "SCC_R":[1.2, 1.5]}



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
        cell = annotation.getElementsByTagName("Cell") # note it's a "list"
        class_i = cell[0].getAttribute("Type")


        # calculate window
        scale = random.uniform(scales[class_i][0], scales[class_i][1])
        w_win = int((x_max - x_min) * scale)
        h_win = int((y_max - y_min) * scale)
        x_win = int((x_min + x_max) / 2 - w_win / 2)
        y_win = int((y_min + y_max) / 2 - h_win / 2)

        labels.append({"class_i":class_i, 
                       "x":x_min, 
                       "y":y_min, 
                       "w":x_max - x_min, 
                       "h":y_max - y_min, 
                       "w_win":w_win, 
                       "h_win":h_win, 
                       "x_win":x_win, 
                       "y_win":y_win})
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
        win_name = "{}_x{}_y{}_w{}_h{}_dx{}_dy{}.bmp".format(basename, 
                                                             label["x"], 
                                                             label["y"], 
                                                             label["w"], 
                                                             label["h"], 
                                                             label["x"]-label["x_win"], 
                                                             label["y"]-label["y_win"])
        win_path = os.path.join(save_path, label["class_i"], win_name)
        os.makedirs(os.path.dirname(win_path), exist_ok=True)
        window.save(win_path)

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