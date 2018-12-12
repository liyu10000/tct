# coding=utf-8
import os
import openslide
import scipy.misc
from xml.dom.minidom import parse
import xml.dom.minidom

from asap_to_labelimg_gen_xml import Xml


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


colors = {"#000000": "MC", "#aa0000": "HSIL", "#aa007f": "ASCH", "#aa00ff": "SC", "#ff0000": "RC",
          "#005500": "LSIL", "#00557f": "ASCUS", "#0055ff": "SCC", "#aa5500": "GEC", "#aa557f": "ADC",
          "#aa55ff": "EC", "#ff5500": "AGC1", "#ff557f": "AGC2", "#ff55ff": "AGC3", "#00aa00": "FUNGI",
          "#00aa7f": "TRI", "#00aaff": "CC", "#55aa00": "ACTINO", "#55aa7f": "VIRUS"}
# colors = {"#aa0000": "HSIL", "#aa007f": "ASCH",
          # "#005500": "LSIL", "#00557f": "ASCUS", "#0055ff": "SCC", "#aa557f": "ADC",
          # "#aa55ff": "EC", "#ff5500": "AGC1", "#ff557f": "AGC2", "#ff55ff": "AGC3", "#00aa00": "FUNGI",
          # "#00aa7f": "TRI", "#00aaff": "CC", "#55aa00": "ACTINO", "#55aa7f": "VIRUS"}

# get coordinates of labels in a xml
def get_labels(xml_file):
    DOMTree = xml.dom.minidom.parse(xml_file)
    collection = DOMTree.documentElement
    annotations = collection.getElementsByTagName("Annotation")

    labels = {}
    i = 0
    for annotation in annotations:
        if annotation.getAttribute("Color") in colors:
            coordinates = annotation.getElementsByTagName("Coordinate")
            x_coords = []
            y_coords = []
            for coordinate in coordinates:
                x_coords.append(float(coordinate.getAttribute("X")))
                y_coords.append(float(coordinate.getAttribute("Y")))                    
            x_min = int(min(x_coords))
            x_max = int(max(x_coords))
            y_min = int(min(y_coords))
            y_max = int(max(y_coords))
            labels[i] = (x_min, x_max, y_min, y_max, colors[annotation.getAttribute("Color")])
            i += 1
    return labels

# get windows in tif that contain labels
def get_windows(labels):
    # # window size is twice the size of label
    # points_xy = {}
    # for i, labelbox in labels.items():
    #     x = int(1.5*labelbox[0] - 0.5*labelbox[1])
    #     y = int(1.5*labelbox[2] - 0.5*labelbox[3])
    #     points_xy[(x, y)] = i
    # return points_xy

    # fixed sized window
    size = 2024
    points_xy = {}
    for i, labelbox in labels.items():
        xcenter = (labelbox[0]+labelbox[1])/2
        ycenter = (labelbox[2]+labelbox[3])/2
        x = int(xcenter - size/2)
        y = int(ycenter - size/2)
        points_xy[(x, y)] = i
    return points_xy
    
def cell_sampling(files_list, save_path):
    for xml_file in files_list:
        labels = get_labels(xml_file)
        print(labels)
        if not labels:
            continue
        points_xy = get_windows(labels)
        print(points_xy)
        
        filename = os.path.splitext(xml_file)[0]
        tif_file = filename + ".tif"
        slide = openslide.OpenSlide(tif_file)
        # generate jpg files      
        for xy, i in points_xy.items():
            size_x = 2*(labels[i][1] - labels[i][0])
            size_y = 2*(labels[i][3] - labels[i][2])
            if size_x < 2 or size_y < 2:
                continue
            cell = slide.read_region(xy, 0, (size_x, size_y))
            cell = cell.convert("RGB")
            scipy.misc.imsave(save_path + "/" + os.path.basename(filename) + "_" + str(xy[0]) + "_" + str(xy[1]) + ".jpg", cell)
        slide.close()
        
        # generate xml files
        new_xmls = Xml(os.path.basename(filename), save_path, points_xy, labels)
        new_xmls.gen_xml()


#classes = ("01_ASCUS", "02_LSIL", "03_ASCH", "04_HSIL", "05_SCC", "06_AGC1", "07_AGC2", "08_ADC", "09_EC", "10_FUNGI", "11_TRI", "12_CC", "13_ACTINO", "14_VIRUS")
classes = ("04_HSIL",)
path_in = os.getcwd()
path_out = os.path.join(path_in, "asap_to_labelimg")
for class_i in classes:
    file_path = os.path.join(path_in, class_i)
    files_list = scan_files(file_path, postfix=".xml")

    save_path = os.path.join(path_out, class_i)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    cell_sampling(files_list, save_path)
