# coding=utf-8
# crop marked region, each at one's center, at a fixed size

import os
import openslide
import scipy.misc
from xml.dom.minidom import parse
import xml.dom.minidom


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


colors = {"#000000": 0,
               "#aa0000": 0,
               "#aa007f": 0,
               "#aa00ff": 0,
               "#ff0000": 0,
               "#005500": 0,
               "#00557f": 0,
               "#0055ff": 0,
               "#aa5500": 0,
               "#aa557f": 0,
               "#aa55ff": 0,
               "#ff5500": 0,
               "#iff557f": 0,
               "#ff55ff": 0,
               "#00aa00": 0,
               "#00aa7f": 0,
               "#00aaff": 0,
               "#55aa00": 0,
               "#55aa7f": 0}


def choose_xy(x_coords, y_coords, size):
    if len(x_coords) < 3:
        return []
    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    x = x_center - size / 2
    y = y_center - size / 2
    return [x, y]


def cellSampling(files_list, save_path, size):
    right = 0
    wrong = 0
    for xml_file in files_list:
        # from .xml filename, get .til filename
        filename = os.path.splitext(xml_file)[0]
        filetype = ".tif"
        # open .tif file
        tif_file = filename + filetype
        try:
            slide = openslide.OpenSlide(tif_file)
            # open .xml file
            DOMTree = xml.dom.minidom.parse(xml_file)
            collection = DOMTree.documentElement
            annotations = collection.getElementsByTagName("Annotation")
            for annotation in annotations:
                if annotation.getAttribute("Color") in colors:
                    coordinates = annotation.getElementsByTagName("Coordinate")
                    # read (x, y) coordinates
                    x_coords = []
                    y_coords = []
                    for coordinate in coordinates:
                        x_coords.append(float(coordinate.getAttribute("X")))
                        y_coords.append(float(coordinate.getAttribute("Y")))
                    # get the (x, y) coordinates for read_region()
                    point_xy = choose_xy(x_coords, y_coords, size)
                    cell = slide.read_region((int(point_xy[0]), int(point_xy[1])), 0, (size, size))
                    cell = cell.convert("RGB")
                    scipy.misc.imsave(save_path + "/" + annotation.getAttribute("Color") + "/" + str(right).zfill(6) + "_data7" + ".jpg", cell)
                    right += 1
                else:
                    wrong += 1
            slide.close()
        except:
            print(filename + " cannot be processed")
    print("# images taken: " + str(right))
    print("# wrong color: " + str(wrong))


file_path = "D:\\data7"
# file_path = "/media/tsimage/Elements/data6"
files_list = scan_files(file_path, postfix=".xml")

save_path = "D:\\0502-data7-size224-jpg"
# save_path = "/media/tsimage/Elements/0430-data1-6-size512"
cellSampling(files_list, save_path, 224)

