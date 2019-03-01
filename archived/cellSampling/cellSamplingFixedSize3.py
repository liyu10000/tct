# coding=utf-8
# for marked region of size no bigger than 600x600 (size may change), clip a fixed-size window (600x600)
# for those bigger than 600x600, first pad it with 100, slide through the broadened region and clip 600x600 windows, with step of 200
# to rule out the case where some windows do not sufficiently overlap with marked region (make a hull out of it this time), we introduce a overlapping factor,
# that only take those windows whose overlapping percentage is no smaller than the factor

# for make hull shell out of given coordinates
from __future__ import division
from numpy import *
import os
import openslide
import scipy.misc

from xml.dom.minidom import parse
import xml.dom.minidom

# for graphical computations
import shapely
from shapely.geometry import Polygon, box

# for make hull shell out of given coordinates
link = lambda a,b: concatenate((a,b[1:]))
edge = lambda a,b: concatenate(([a],[b]))

def qhull2D(sample):
    def dome(sample, base):
        h, t = base
        dists = dot(sample-h, dot(((0,-1),(1,0)),(t-h)))
        outer = repeat(sample, dists>0, 0)
        if len(outer):
            pivot = sample[argmax(dists)]
            return link(dome(outer, edge(h, pivot)),
                    dome(outer, edge(pivot, t)))
        else:
            return base
    if len(sample) > 2:
        axis = sample[:,0]
        base = take(sample, [argmin(axis), argmax(axis)], 0)
        return link(dome(sample, base), dome(sample, base[::-1]))
    else:
        return sample


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


def is_overlapped(marked, window, factor):
    # print(marked.intersection(window).area / window.area)
    if marked.intersection(window).area / window.area >= factor:
        return True
    else:
        return False

def choose_xy(coords_xy, size, factor):
    # get a polygon object from coords_xy
    hull_xy = qhull2D(array(coords_xy))
    coords_xy_2 = [tuple(point) for point in hull_xy ]
    # if len(coords_xy_2) < 3:  # avoid the case of single dots
    #     return []
    marked = Polygon(coords_xy_2)
    # marked = Polygon(marked.exterior.coords)  # not useful

    # get mininum-area-bounding-rectangle
    x_min = min([coord_xy[0] for coord_xy in coords_xy])
    x_max = max([coord_xy[0] for coord_xy in coords_xy])
    y_min = min([coord_xy[1] for coord_xy in coords_xy])
    y_max = max([coord_xy[1] for coord_xy in coords_xy])

    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    x_span = x_max - x_min
    y_span = y_max - y_min

    points_xy = []

    if x_span <= size and y_span <= size:
        points_xy.append([x_center - size / 2, y_center - size / 2])
    # if marked region is too big, slide through x & y direction, 200 each step
    else:
        # print(x_center, y_center, x_span, y_span)
        padding = 10
        pace = 128
        x = x_min - padding
        y = y_min - padding
        while x + size <= x_max + padding:
            # take a block
            window = box(x, y, x+size, y+size)
            if (is_overlapped(marked, window, factor)):
                points_xy.append([x, y])
            curr_y = y
            while y + size <= y_max + padding:
                y += pace
                # take a block
                window = box(x, y, x + size, y + size)
                if (is_overlapped(marked, window, factor)):
                    points_xy.append([x, y])
            y = curr_y
            x += pace

        while y + size <= y_max + padding:
            # take a block
            window = box(x, y, x + size, y + size)
            if (is_overlapped(marked, window, factor)):
                points_xy.append([x, y])
            y += pace

        # special case: marked region is big enough, but does not have sufficient overlapping for crop
        if not points_xy:
            points_xy.append([x_center - size / 2, y_center - size / 2])

    return points_xy


def cellSampling(files_list, save_path, size, factor):
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
                #if annotation.getAttribute("Color") in colors:
                if annotation.getAttribute("Color") == "#00557f":
                    coordinates = annotation.getElementsByTagName("Coordinate")

                    # read (x, y) coordinates
                    coords_xy = []
                    for coordinate in coordinates:
                        coords_xy.append([float(coordinate.getAttribute("X")), float(coordinate.getAttribute("Y"))])

                    # stores the (x, y) coordinates for read_region()
                    points_xy = choose_xy(coords_xy, size, factor)
                    for point_xy in points_xy:
                        cell = slide.read_region((int(point_xy[0]), int(point_xy[1])), 0, (size, size))
                        cell = cell.convert("RGB")
                        # scipy.misc.imsave(save_path + "/" + annotation.getAttribute("Color") + "/" + str(right).zfill(6) + "_" + filename[3:].replace("\\", "_") + "_" + annotation.getAttribute("Name") + ".jpeg", cell)
                        scipy.misc.imsave(save_path + "/" + annotation.getAttribute("Color") + "/" + str(right).zfill(6) + "_data8_0515" + ".jpg", cell)
                        right += 1

                else:
                    wrong += 1

            slide.close()

        except:
            print(filename + " cannot be processed")

    print("# images taken: " + str(right))
    print("# wrong color: " + str(wrong))


file_path = "F:\\data8"
# file_path = "/media/tsimage/Elements/data6"
files_list = scan_files(file_path, postfix=".xml")

save_path = "F:\\0514-data1-8-size256"
# save_path = "/media/tsimage/Elements/0427-data1-6-size224"
size = 256
fill_factor = 0.8
cellSampling(files_list, save_path, size, fill_factor)



