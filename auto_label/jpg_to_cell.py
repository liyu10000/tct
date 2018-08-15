# coding=utf-8
# crop out the marked region, as it is

import os
import numpy as np
from PIL import Image
from xml.dom.minidom import parse
import xml.dom.minidom

# classes = {"HSIL":0, "ASCH":0, "LSIL":0, "ASCUS":0, "SCC":0, "ADC":0, "EC":0, 
#            "AGC1":0, "MC":0, "SC":0, "RC":0, "GEC":0, "AGC2":0, "AGC3":0, 
#            "FUNGI":0, "TRI":0, "CC":0, "ACTINO":0, "VIRUS":0}
# classes = {"HSIL":0, "ASCH":0, "LSIL":0, "ASCUS":0, "SCC":0}

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

def resize_img(img, size):
    img_croped = img.crop(
        (
            -((size - img.size[0]) / 2),
            -((size - img.size[1]) / 2),
            img.size[0] + (size - img.size[0]) / 2,
            img.size[1] + (size - img.size[1]) / 2
        )
    )
    img_resized = img_croped.resize((size, size))
    return img_resized

def get_cells(files_list, classes, size):
    """
    return:
        numpy array
        cell_numpy_index: {index:(x_y_i, class_i)}
    """
    cell_list = []
    cell_numpy_index = {}
    index = 0
    for xml_file in files_list:
        # from .xml filename, get .tif filename
        filename = os.path.splitext(xml_file)[0]
        filetype = ".jpg"
        # open .jpg file
        jpg_file = filename + filetype
        # try:
        image = Image.open(jpg_file)
        # open .xml file
        DOMTree = xml.dom.minidom.parse(xml_file)
        collection = DOMTree.documentElement
        width = collection.getElementsByTagName("width")[0].firstChild.nodeValue
        height = collection.getElementsByTagName("height")[0].firstChild.nodeValue
        objects = collection.getElementsByTagName("object")
        i = 0
        for object_i in objects:
            name = object_i.getElementsByTagName("name")[0].firstChild.nodeValue
            xmin = int(object_i.getElementsByTagName("xmin")[0].firstChild.nodeValue)
            ymin = int(object_i.getElementsByTagName("ymin")[0].firstChild.nodeValue)
            xmax = int(object_i.getElementsByTagName("xmax")[0].firstChild.nodeValue)
            ymax = int(object_i.getElementsByTagName("ymax")[0].firstChild.nodeValue)
            if name in classes:
                classes[name] += 1
                # cell_path = os.path.join(save_path, name)
                # if not os.path.exists(cell_path):
                #     os.makedirs(cell_path)
                #cell_name = os.path.join(cell_path, os.path.basename(filename)+"_"+str(i)+".jpg")
                cell_name = os.path.basename(filename)+"_"+str(i)
                cell_numpy_index[index] = (cell_name, name)
                index += 1
                #print(name, xmin, ymin, xmax, ymax)
                #image.crop((xmin, ymin, xmax, ymax)).save(cell_name)
                cell_list.append(np.array(resize_img(image.crop((xmin, ymin, xmax, ymax)), size)))
            i += 1
        image.close()
        # except:
        #     print(filename + " cannot be processed")
        
    return np.asarray(cell_list), cell_numpy_index


if __name__ == "__main__":
    classes = {"HSIL":0, "ASCH":0, "LSIL":0, "ASCUS":0, "SCC":0}
    file_path = "/home/sakulaki/dataset/realtest/608/XB1800118"
    # save_path = "/home/sakulaki/dataset/realtest/608/XB1800118_cells"
    # if not os.path.exists(save_path):
    #     os.makedirs(save_path)
    files_list = scan_files(file_path, postfix=".xml")
    size = 299
    get_cells(files_list, classes, size)
    print(sorted(classes.items()))
