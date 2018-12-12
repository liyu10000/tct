# crops images surrounding marked region, top, bottom, left and right

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
               "#ff557f": 0,
               "#ff55ff": 0,
               "#00aa00": 0,
               "#00aa7f": 0,
               "#00aaff": 0,
               "#55aa00": 0,
               "#55aa7f": 0}


def read_coords_all(xml_file):
    coords_all = []
    DOMTree = xml.dom.minidom.parse(xml_file)
    collection = DOMTree.documentElement
    annotations = collection.getElementsByTagName("Annotation")

    for annotation in annotations:
        if annotation.getAttribute("Color") in colors:
            coordinates = annotation.getElementsByTagName("Coordinate")
            coords_one = []
            for coordinate in coordinates:
                coords_one.append((float(coordinate.getAttribute("X")), float(coordinate.getAttribute("Y"))))
            coords_all.append(coords_one)

    return coords_all


def isOverlapped(coords_curr, coords_all):
    # coords_curr: [x_1, x_2, y_1, y_2]
    for coords_one in coords_all:
        for coords_xy in coords_one:
            if coords_curr[0] < coords_xy[0] < coords_curr[1] and coords_curr[2] < coords_xy[1] < coords_curr[3]:
                return True
    return False


def choose_xy(coords_one, size, coords_all):
    # get mininum-area-bounding-rectangle
    x_min = min([coord_xy[0] for coord_xy in coords_one])
    x_max = max([coord_xy[0] for coord_xy in coords_one])
    y_min = min([coord_xy[1] for coord_xy in coords_one])
    y_max = max([coord_xy[1] for coord_xy in coords_one])

    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2

    points_xy = []
    four_xy = []

    # top
    x_1 = x_center - size/2
    y_1 = y_min - size
    four_xy.append([x_1, y_1])
    # bottom
    x_1 = x_center - size/2
    y_1 = y_max
    four_xy.append([x_1, y_1])
    # left
    x_1 = x_min - size
    y_1 = y_center - size/2
    four_xy.append([x_1, y_1])
    # right
    x_1 = x_max
    y_1 = y_center - size/2
    four_xy.append([x_1, y_1])

    for one_xy in four_xy:
        if not isOverlapped([one_xy[0], one_xy[0]+size, one_xy[1], one_xy[1]+size], coords_all):
            points_xy.append(one_xy)

    return points_xy


def cellSampling(files_list, save_path, size):
    right = 0
    wrong = 0
    for xml_file in files_list:
        # from .xml filename, get .til filename
        filename = os.path.splitext(xml_file)[0]
        filetype = ".tif"

        coords_all = read_coords_all(xml_file)

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
                    coords_xy = []
                    for coordinate in coordinates:
                        coords_xy.append((float(coordinate.getAttribute("X")), float(coordinate.getAttribute("Y"))))
                    # stores the (x, y) coordinates for read_region()
                    points_xy = choose_xy(coords_xy, size, coords_all)
                    for point_xy in points_xy:
                        cell = slide.read_region((int(point_xy[0]), int(point_xy[1])), 0, (size, size))
                        cell = cell.convert("RGB")
                        cropped_file = save_path + "\\" + str(right).zfill(8) + ".jpg"
                        scipy.misc.imsave(cropped_file, cell)
                        right += 1
                else:
                    wrong += 1

            slide.close()

        except:
            print(filename + " cannot be processed")

    print("# images taken: " + str(right))
    print("# wrong color: " + str(wrong))


if __name__ == "__main__":
    files_path = "D:\\0414-annotated"
    files_list = scan_files(files_path, postfix=".xml")
    save_path = "D:\\0414-annotated-size512-crops"

    size = 512
    cellSampling(files_list, save_path, size)



