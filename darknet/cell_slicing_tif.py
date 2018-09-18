# coding=utf-8
import os
import openslide
import scipy.misc
import xml.dom.minidom

from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed
from tslide.tslide import TSlide

from gen_xml import Xml


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


# classes = {"#000000": "MC", "#aa0000": "HSIL", "#aa007f": "ASCH", "#aa00ff": "SC", "#ff0000": "RC",
#           "#005500": "LSIL", "#00557f": "ASCUS", "#0055ff": "SCC", "#aa5500": "GEC", "#aa557f": "ADC",
#           "#aa55ff": "EC", "#ff5500": "AGC1", "#ff557f": "AGC2", "#ff55ff": "AGC3", "#00aa00": "FUNGI",
#           "#00aa7f": "TRI", "#00aaff": "CC", "#55aa00": "ACTINO", "#55aa7f": "VIRUS"}
classes = {"#aa0000": "HSIL", "#aa007f": "ASCH",
          "#005500": "LSIL", "#00557f": "ASCUS", "#0055ff": "SCC", "#aa557f": "ADC",
          "#aa55ff": "EC", "#ff5500": "AGC1", "#ff557f": "AGC2", "#ff55ff": "AGC3", "#00aa00": "FUNGI",
          "#00aa7f": "TRI", "#00aaff": "CC", "#55aa00": "ACTINO", "#55aa7f": "VIRUS"}

# get coordinates of labels in a xml
def get_labels(xml_file):
    """
        xml_file: single xml file for tif
        return: {i:(x_min, x_max, y_min, y_max, color)}
    """
    DOMTree = xml.dom.minidom.parse(xml_file)
    collection = DOMTree.documentElement
    annotations = collection.getElementsByTagName("Annotation")

    labels = {}
    i = 0
    for annotation in annotations:
        if annotation.getAttribute("Color") in classes:
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
            labels[i] = (x_min, x_max, y_min, y_max, classes[annotation.getAttribute("Color")])
            i += 1
    return labels

# get windows in tif that contain labels
def get_windows(labels, size_x, size_y, size):
    """
        labels: {i:(x_min, x_max, y_min, y_max, color)}
        size_x, size_y: dimensions of 0th layer of tif
        size: image size to crop
        return: {(x, y):[i,]}
    """
    points_xy = {}
    x, y = 0, 0
    while x + size <= size_x:
        while y + size <= size_y:
            for i, label in labels.items():
                if (x <= label[0] and label[1] <= x+size and y <= label[2] and label[3] <= y+size) or \
                   ((label[0] <= x and x+size <= label[1]) and (label[2] <= y and y+size <= label[3])) or \
                   ((label[0] <= x and x+size <= label[1]) and (y <= label[2] and label[3] <= y+size)) or \
                   ((x <= label[0] and label[1] <= x+size) and (label[2] <= y and y+size <= label[3])):
                    if (x, y) in points_xy:
                        points_xy[(x, y)].append(i)
                    else:
                        points_xy[(x, y)] = [i,]
            y += 200
        y = 0
        x += 200
    
    # remove duplicates
    points_xy_new = {}
    for key, value in points_xy.items():
        if value not in points_xy_new.values():
            points_xy_new[key] = value  
    # remove subsets
    points_xy_copy = {key:value for key,value in points_xy_new.items()}
    to_delete = []
    for key2, value2 in points_xy_copy.items():
        for key, value in points_xy_new.items():
            if key != key2 and set(value).issubset(set(value2)):
                to_delete.append(key)
    for key in to_delete:
        if key in points_xy_new:
            points_xy_new.pop(key)
    
    return points_xy_new

    
def cell_sampling(xml_file, save_path, size):
    labels = get_labels(xml_file)
    # print(labels)
    
    filename = os.path.splitext(xml_file)[0]
    if (not os.path.isfile(filename+".tif")) and (not os.path.isfile(filename+".kfb")):
        print(filename + " doesn't exist")
        return
    try:
        slide = openslide.OpenSlide(filename+".tif")
    except:
        slide = TSlide(filename+".kfb")
    
    size_x, size_y = slide.dimensions
    points_xy = get_windows(labels, size_x, size_y, size)
    # print(points_xy)
    
    # generate jpg files      
    for (x, y) in points_xy:
        cell = slide.read_region((x, y), 0, (size, size)).convert("RGB")
        cell.save(save_path + "/" + os.path.basename(filename) + "_" + str(x) + "_" + str(y) + ".jpg")

    slide.close()
    
    # generate xml files
    new_xmls = Xml(os.path.basename(filename), save_path, points_xy, labels, size)
    new_xmls.gen_xml()

    print("processed ", xml_file)


def cut_cells(path_in, path_out, size):
    sub_dirs = os.listdir(path_in)
    for sub_dir in sub_dirs:
        file_path_i = os.path.join(path_in, sub_dir)
        xml_files = scan_files(file_path_i, postfix=".xml")
        save_path_i = os.path.join(path_out, sub_dir)
        os.makedirs(save_path_i, exist_ok=True)

        executor = ProcessPoolExecutor(max_workers=cpu_count() - 4)
        tasks = []
        for xml_file in xml_files:
            tasks.append(executor.submit(cell_sampling, xml_file, save_path_i, size))
        
        job_count = len(tasks)
        for future in as_completed(tasks):
            # result = future.result()  # get the returning result from calling fuction
            job_count -= 1
            # print("One Job Done, last Job Count: %s" % (job_count))



if __name__ == "__main__":
    file_path = "/media/tsimage/Elements/data"
    save_path = "/media/tsimage/Elements/data/tct_data608_0716"
    cut_cells(file_path, save_path, 608)

