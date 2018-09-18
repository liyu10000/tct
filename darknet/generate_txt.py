import os
import xml.etree.ElementTree as ET

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
    
def _gen_txt(xml_name, txt_path):
    txt_name = os.path.splitext(os.path.basename(xml_name))[0] + ".txt"
    txt_file = open(os.path.join(txt_path, txt_name), "w")
    tree = ET.parse(xml_name)
    root = tree.getroot()
    size = root.find("size")
    w = int(size.find("width").text)
    h = int(size.find("height").text)
    
    for object_i in root.iter("object"):
        name = object_i.find("name").text
        if not name in classes:
            continue
        index = classes[name]
        bndbox = object_i.find('bndbox')
        box = (float(bndbox.find('xmin').text), float(bndbox.find('xmax').text), float(bndbox.find('ymin').text), float(bndbox.find('ymax').text))
        box_new = ((box[0]+box[1])/2.0/w, (box[2]+box[3])/2.0/h, (box[1]-box[0])/w, (box[3]-box[2])/h)
        txt_file.write(str(index) + " " + " ".join([str(a) for a in box_new]) + "\n")
    txt_file.close()


def gen_txt(path, dirs=("train", "valid", "test")):
    for d in dirs:
        xml_names = scan_files(os.path.join(path, d), postfix=".xml")
        txt_file = open(os.path.join(path, d+".txt"), "w")
        for xml_name in xml_names:
            jpg_name = os.path.splitext(xml_name)[0] + ".jpg"
            _gen_txt(xml_name, os.path.dirname(xml_name))
            txt_file.write(jpg_name+"\n")
        txt_file.close()
    
if __name__ == "__main__":
    #generate txt_list for a folder
    path = ""
    gen_txt(path)
