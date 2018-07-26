import os
from random import shuffle
import xml.etree.ElementTree as ET
from shutil import copy2, move

# # 6 classes
# classes = {"ASCUS":0, "LSIL":0, "ASCH":1, "HSIL":1, "SCC":2, "AGC1":1, "AGC2":1,
           # "ADC":1, "EC":1, "FUNGI":4, "TRI":2, "CC":0, "ACTINO":5, "VIRUS":3}

# 14 classes
classes = {"ASCUS":0, "LSIL":1, "ASCH":2, "HSIL":3, "SCC":4, "AGC1":5, "AGC2":6,
           "ADC":7, "EC":8, "FUNGI":9, "TRI":10, "CC":11, "ACTINO":12, "VIRUS":13}
           
# # 5 classes
# classes = {"ASCUS":0, "LSIL":1, "ASCH":2, "HSIL":3, "SCC":4}

# # 1 class
# classes = {"ASCUS":0}

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
    
def gen_txt(xml_name, txt_path):
    txt_name = os.path.splitext(os.path.basename(xml_name))[0] + ".txt"
    txt_file = open(os.path.join(txt_path, txt_name), "w")
    tree = ET.parse(xml_name)
    root = tree.getroot()
    size = root.find("size")
    w = int(size.find("width").text)
    h = int(size.find("height").text)
    
    for object in root.iter("object"):
        name = object.find("name").text
        if not name in classes:
            continue
        index = classes[name]
        bndbox = object.find('bndbox')
        box = (float(bndbox.find('xmin').text), float(bndbox.find('xmax').text), float(bndbox.find('ymin').text), float(bndbox.find('ymax').text))
        box_new = ((box[0]+box[1])/2.0/w, (box[2]+box[3])/2.0/h, (box[1]-box[0])/w, (box[3]-box[2])/h)
        txt_file.write(str(index) + " " + " ".join([str(a) for a in box_new]) + "\n")
    txt_file.close()

def gen_txt_and_separate(xml_names, factor):
    n_val = int(len(xml_names)*factor)
    print("# train: " + str(len(xml_names) - n_val))
    print("# validate: " + str(n_val))
    shuffle(xml_names)
    save_path = os.getcwd()
    train = open(os.path.join(save_path, "train.txt"), "w")
    validate = open(os.path.join(save_path, "validate.txt"), "w")
    train_path = os.path.join(save_path, "train")
    if not os.path.exists(train_path):
        os.makedirs(train_path)
    validate_path = os.path.join(save_path, "validate")
    if not os.path.exists(validate_path):
        os.makedirs(validate_path)
    i = 0
    for xml_name in xml_names:
        jpg_name = os.path.splitext(xml_name)[0] + ".jpg"
        basename = os.path.basename(xml_name)
        if i < n_val:
            move(jpg_name, validate_path)
            move(xml_name, validate_path)
            # copy2(jpg_name, validate_path)
            # gen_txt(xml_name, validate_path)
            # validate.write(os.path.join(validate_path, basename) + "\n")
        # else:
            # copy2(jpg_name, train_path)
            # gen_txt(xml_name, train_path)
            # train.write(os.path.join(train_path, basename) + "\n")
        i += 1
    train.close()
    validate.close()
    
def gen_txt_only(xml_names, path, dir):
    shuffle(xml_names)
    save_path = os.path.join(path, dir)
    txt_file = open(os.path.join(path, dir+".txt"), "w")
    for xml_name in xml_names:
        jpg_name = os.path.splitext(xml_name)[0] + ".jpg"
        gen_txt(xml_name, save_path)
        txt_file.write(jpg_name+"\n")
    txt_file.close()
        
    
if __name__ == "__main__":
    #generate txt_list for a folder
    path = os.getcwd()
    dirs = ("train", "validate", "test")
    for dir in dirs:
        xml_names = scan_files(os.path.join(path, dir), postfix=".xml")
        gen_txt_only(xml_names, path, dir)
    
    # # separate data into train/validate sets and generate txt_list
    # path = os.path.join(os.getcwd(), "train")
    # factor = 0.1
    # xml_names = scan_files(path, postfix=".xml")
    # gen_txt_and_separate(xml_names, factor)
    
