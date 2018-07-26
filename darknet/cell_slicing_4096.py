# coding=utf-8
import os
from PIL import Image

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

colors = {"MC":0, "HSIL":0, "ASCH":0, "SC":0, "RC":0,
          "LSIL":0, "ASCUS":0, "SCC":0, "GEC":0, "ADC":0,
          "EC":0, "AGC1":0, "AGC2":0, "AGC3":0, "FUNGI":0,
          "TRI":0, "CC":0, "ACTINO":0, "VIRUS":0}

def get_labels(txt_file):
    # open .txt file
    txt = open(txt_file, "r")
    labels = {}
    i = 0
    for line in txt:
        tokens = line.strip().split(",")
        labels[i] = (int(tokens[0]), int(tokens[0])+int(tokens[2]), int(tokens[1]), int(tokens[1])+int(tokens[3]), tokens[4])
        colors[tokens[4]] += 1
        i += 1
    txt.close() 
    return labels
          
def get_windows(labels, size_x, size_y, size):
    points_xy = {}
    x, y = 0, 0
    while x + size <= size_x:
        while y + size <= size_y:
            for i, label in labels.items():
                if (x <= label[0] and label[1] <= x+size and y <= label[2] and label[3] <= y+size) or ((label[0] <= x and x+size <= label[1]) and (label[2] <= y and y+size <= label[3])) or ((label[0] <= x and x+size <= label[1]) and (y <= label[2] and label[3] <= y+size)) or ((x <= label[0] and label[1] <= x+size) and (label[2] <= y and y+size <= label[3])):
                    if (x, y) in points_xy:
                        points_xy[(x, y)].append(i)
                    else:
                        points_xy[(x, y)] = [i,]
            y += 100
        y = 0
        x += 100
    
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
          
def cellSampling(files_list, save_path, size):
    for txt_file in files_list:
        # from .txt filename, get .jpg filename
        filename = os.path.splitext(txt_file)[0]

        # open .txt file
        labels = get_labels(txt_file)   
        print(labels)

        # open .jpg file
        img_file = filename + ".jpg"
        img = Image.open(img_file)
        
        size_x, size_y = img.size
        points_xy = get_windows(labels, size_x, size_y, size)
        print(points_xy)
        
        # generate jpg files
        for (x, y) in points_xy:
            img.crop((x, y, x+size, y+size)).save(save_path + "/" + os.path.basename(filename) + "_" + str(x) + "_" + str(y) + ".jpg")
            
        img.close()
        
        # generate xml files
        new_xmls = Xml(os.path.basename(filename), save_path, points_xy, labels, size)
        new_xmls.gen_xml()


file_path = os.path.join(os.getcwd(), "4096")
files_list = scan_files(file_path, postfix=".txt")

save_path = os.path.join(os.getcwd(), "test3")
if not os.path.exists(save_path):
    os.makedirs(save_path)
cellSampling(files_list, save_path, 608)
print()
print(colors)



