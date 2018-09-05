# coding=utf-8
# crop marked region, place labeled box in a fixed sized image, at specified position

import os
import openslide
import scipy.misc
from xml.dom.minidom import parse
import xml.dom.minidom


colors = {"#aa0000": "HSIL", "#aa007f": "ASCH", "#005500": "LSIL", "#00557f": "ASCUS", 
          "#0055ff": "SCC", "#aa557f": "ADC", "#aa55ff": "EC", "#ff5500": "AGC1", 
          "#ff557f": "AGC2", "#ff55ff": "AGC3", "#00aa00": "FUNGI", "#00aa7f": "TRI", 
          "#00aaff": "CC", "#55aa00": "ACTINO", "#55aa7f": "VIRUS",
          "#000000": "MC", "#aa00ff": "SC", "#ff0000": "RC", "#aa5500": "GEC"}


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


def get_xy(box, size, position):
    """
    cut image out of label box.
    note: label box should be within image
    :params box: (xmin, ymin, xmax, ymax)
    :params size: image size to cut out
    :params position: (x_percent, y_percent), the center of label box relative to image.
                      if need to put label box in center of image, set position to (0.5, 0.5)
    :return: the upper-left coordinates (x, y) of image. if anything wrong happens, return (-1, -1)
    """
    box_center_x = (box[0]+box[2])/2
    box_center_y = (box[1]+box[3])/2
    x = box_center_x - size*position[0]
    y = box_center_y - size*position[1]
    if x > box[0] or y > box[1] or x+size < box[2] or y+size < box[3]:
        return (-1, -1)
    return (int(x), int(y))


def cut_cells(xml_file, save_path, size, position):
    # get basename, without extension
    basename = os.path.splitext(os.path.basename(xml_file))[0]
    # open .tif file
    tif_file = os.path.join(os.path.dirname(xml_file), basename+".tif")
    count = 0
    slide = openslide.OpenSlide(tif_file)
    # open .xml file
    DOMTree = xml.dom.minidom.parse(xml_file)
    collection = DOMTree.documentElement
    annotations = collection.getElementsByTagName("Annotation")
    for annotation in annotations:
        if annotation.getAttribute("Color") in colors:
            coordinates = annotation.getElementsByTagName("Coordinate")
            # read (x, y) coordinates
            x_coords = [float(coordinate.getAttribute("X")) for coordinate in coordinates]
            y_coords = [float(coordinate.getAttribute("Y")) for coordinate in coordinates]
            if len(x_coords) < 3:
                continue
            # get the (x, y) coordinates for read_region()
            x, y = get_xy((min(x_coords), min(y_coords), max(x_coords), max(y_coords)), size, position)
            if x == -1:
                continue
            save_path_i = os.path.join(save_path, basename, colors[annotation.getAttribute("Color")])
            os.makedirs(save_path_i, exist_ok=True)
            cell = slide.read_region((x, y), 0, (size, size)).convert("RGB")
            cell.save(os.path.join(save_path_i, "{}_{}_{}.jpg".format(basename, x, y)))
            count += 1
    slide.close()
    print(basename + ": number of cells " + str(count))


def batch_process(path_in, path_out, size, position):
    files_list = scan_files(path_in, postfix=".xml")
    for f in files_list:
        cut_cells(f, path_out, size, position)


if __name__ == "__main__":
    path_in = "/home/sakulaki/yolo-yuli/one_stop_test/tif_xml"
    path_out = "/home/sakulaki/yolo-yuli/one_stop_test/tif_xml_cells"
    batch_process(path_in, path_out, 512, (0.5, 0.5))    

