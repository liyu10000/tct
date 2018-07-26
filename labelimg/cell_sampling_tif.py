# coding=utf-8
# clip two times the size of marked region

import os
import openslide
import scipy.misc
from xml.dom.minidom import parse
import xml.dom.minidom

colors = {"#000000": "MC", "#aa0000": "HSIL", "#aa007f": "ASCH", "#aa00ff": "SC", "#ff0000": "RC", "#005500": "LSIL", 
          "#00557f": "ASCUS", "#0055ff": "SCC", "#aa5500": "GEC", "#aa557f": "ADC", "#aa55ff": "EC", "#ff5500": "AGC1", 
          "#ff557f": "AGC2", "#ff55ff": "AGC3", "#00aa00": "FUNGI", "#00aa7f": "TRI", "#00aaff": "CC", 
          "#55aa00": "ACTINO", "#55aa7f": "VIRUS"}

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

def cellSampling(files_list, save_path):
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

            i = 0
            for annotation in annotations:
                coordinates = annotation.getElementsByTagName("Coordinate")

                # read (x, y) coordinates
                x_coords = []
                y_coords = []
                for coordinate in coordinates:
                    x_coords.append(float(coordinate.getAttribute("X")))
                    y_coords.append(float(coordinate.getAttribute("Y")))

                # get mininum-area-bounding-rectangle
                x_min = min(x_coords)
                x_max = max(x_coords)
                y_min = min(y_coords)
                y_max = max(y_coords)

                # # 2 times the size of marked region
                # x = int(1.5 * x_min - 0.5 * x_max)
                # y = int(1.5 * y_min - 0.5 * y_max)
                # x_size = int(2 * (x_max - x_min))
                # y_size = int(2 * (y_max - y_min))

                # take out the size as it is
                x = int(x_min)
                y = int(y_min)
                x_size = int(x_max - x_min)
                y_size = int(y_max - y_min)

                if annotation.getAttribute("Color") in colors:
                    cell = slide.read_region((x, y), 0, (x_size, y_size)).convert("RGB")
                    cell_path = os.path.join(save_path, colors[annotation.getAttribute("Color")])
                    if not os.path.exists(cell_path):
                        os.makedirs(cell_path)
                    cell_name = os.path.join(cell_path, os.path.basename(filename)+"_"+str(i)+".jpg")
                    scipy.misc.imsave(cell_name, cell)
                i += 1

            slide.close()

        except:
            print(filename + " cannot be processed")


if __name__ == "__main__":
    file_path = "/media/tsimage/Elements/data/asap_all"
    save_path = "/media/tsimage/Elements/data/tct_data_samesize_0718"
    files_list = scan_files(file_path, postfix=".xml")
    cellSampling(files_list, save_path)
