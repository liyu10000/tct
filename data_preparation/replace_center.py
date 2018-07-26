# replace center (marked region) of an image with a same sized section from another image
import os
import cv2
import openslide
from random import randint
import xml.dom.minidom
import numpy as np
from utils.scan_files import scan_files

# # test
# dest = cv2.imread("../res/temp/minions.jpg")
# height, width, channels = dest.shape
# print(height, width, channels)
# print(dest.dtype)
#
# src = cv2.imread("../res/temp/minions.jpg")
# dest[0:int(height/2), 0:int(width/2)] = src[int(height/2):height, int(width/2):width]
# status = cv2.imwrite("../res/temp/minions_1.jpg", dest)
# if not status:
#     print("error")

src_image_path = "F:\\data0\\2018-04-08-normal-crops"
src_image_size = 4096
src_images = scan_files(src_image_path)

tif_path = "F:\\data8\\11_TRI"
des_image_path1 = "F:\\0514-data1-8-replace2normal-size256\\replace2normal_1"
des_image_path2 = "F:\\0514-data1-8-replace2normal-size256\\replace2normal_2"
des_image_path3 = "F:\\0514-data1-8-replace2normal-size256\\replace2normal_3"
des_image_size = 256

colors = {"#000000": 0, "#aa0000": 0, "#aa007f": 0, "#aa00ff": 0, "#ff0000": 0, "#005500": 0, "#00557f": 0,
          "#0055ff": 0, "#aa5500": 0, "#aa557f": 0, "#aa55ff": 0, "#ff5500": 0, "#ff557f": 0, "#ff55ff": 0,
          "#00aa00": 0, "#00aa7f": 0, "#00aaff": 0, "#55aa00": 0, "#55aa7f": 0}


def get_random_image(x_size, y_size):
    chosen = randint(0, len(src_images)-1)
    x = randint(0, src_image_size - x_size)
    y = randint(0, src_image_size - y_size)
    src_image = cv2.imread(src_images[chosen])
    return src_image[y:y+y_size, x:x+x_size]
    # minions = cv2.imread("../res/temp/minions.jpg")
    # height, width, channels = minions.shape
    # x = width/2
    # y = height/2
    # return minions[int(y-y_size/2):int(y+y_size/2), int(x-x_size/2):int(x+x_size/2)]


def replace():
    files_list = scan_files(tif_path, postfix=".xml")
    total = 0
    replaced = 0
    for xml_file in files_list:
        # from .xml filename, get .til filename
        filename = os.path.splitext(xml_file)[0]
        name = filename.rsplit("\\", 1)[1]
        # open .tif file
        tif_file = filename + ".tif"
        slide = openslide.OpenSlide(tif_file)

        # open .xml file
        DOMTree = xml.dom.minidom.parse(xml_file)
        collection = DOMTree.documentElement
        annotations = collection.getElementsByTagName("Annotation")

        for annotation in annotations:
            coordinates = annotation.getElementsByTagName("Coordinate")

            # read (x, y) coordinates
            x_coords = []
            y_coords = []
            for coordinate in coordinates:
                x_coords.append(float(coordinate.getAttribute("X")))
                y_coords.append(float(coordinate.getAttribute("Y")))
            if len(x_coords) < 3:
                continue
            x_min = min(x_coords)
            x_max = max(x_coords)
            y_min = min(y_coords)
            y_max = max(y_coords)
            x_size = int(x_max - x_min)
            y_size = int(y_max - y_min)
            x_min = int(x_min)
            y_min = int(y_min)
            x = int((x_min+x_max)/2 - des_image_size/2)
            y = int((y_min+y_max)/2 - des_image_size/2)

            # marked region is small, can be replaced
            if annotation.getAttribute("Color") in colors and x_size < des_image_size and y_size < des_image_size:
                print("marked region size: " + str(x_size) + ", " + str(y_size))
                cell = slide.read_region((x, y), 0, (des_image_size, des_image_size))
                cell = cv2.cvtColor(np.asarray(cell), cv2.COLOR_RGBA2BGR)
                cell[y_min - y:y_min - y + y_size, x_min - x:x_min - x + x_size] = get_random_image(x_size, y_size)
                cv2.imwrite(des_image_path1 + "\\" + name + "_" + annotation.getAttribute("Name") + "_replaced1_tri_0514.jpg", cell)
                cell[y_min - y:y_min - y + y_size, x_min - x:x_min - x + x_size] = get_random_image(x_size, y_size)
                cv2.imwrite(des_image_path2 + "\\" + name + "_" + annotation.getAttribute("Name") + "_replaced2_tri_0514.jpg", cell)
                cell[y_min - y:y_min - y + y_size, x_min - x:x_min - x + x_size] = get_random_image(x_size, y_size)
                cv2.imwrite(des_image_path3 + "\\" + name + "_" + annotation.getAttribute("Name") + "_replaced3_tri_0514.jpg", cell)
                replaced += 1
            total += 1

        slide.close()

    print("# total images: " + str(total))
    print("# replaced: " + str(replaced))

if __name__ == "__main__":
    replace()
