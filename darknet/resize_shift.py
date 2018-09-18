import os
from shutil import copy2
import xml.dom.minidom
from random import randint, uniform, shuffle

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

def resize(xmin, ymin, xmax, ymax, factor):
    """
        factor: (0.8~1.2)
    """
    xcenter = (xmin + xmax)/2
    ycenter = (ymin + ymax)/2
    xmin_new = int(xmin - (factor-1.0)*(xcenter-xmin))
    ymin_new = int(ymin - (factor-1.0)*(ycenter-ymin))
    xmax_new = int(xmax + (factor-1.0)*(xcenter-xmin))
    ymax_new = int(ymax + (factor-1.0)*(ycenter-ymin))
    return (xmin_new, ymin_new, xmax_new, ymax_new)
    
def shift(xmin, ymin, xmax, ymax, direction, factor):
    """
        direction: 0(up&down), 1(left&right)
        factor: (0.8~1.2), up/left if > 1.0
    """
    if direction == 0:
        shift_size = (factor-1.0)*(ymax-ymin)
        return (xmin, int(ymin-shift_size), xmax, int(ymax-shift_size))
    else:
        shift_size = (factor-1.0)*(xmax-xmin)
        return (int(xmin-shift_size), ymin, int(xmax-shift_size), ymax)

def process(xml_name, class_i):
    jpg_name = os.path.splitext(xml_name)[0] + ".jpg"
    DOMTree = xml.dom.minidom.parse(xml_name)
    collection = DOMTree.documentElement
    filename = collection.getElementsByTagName("filename")
    objects = collection.getElementsByTagName("object")
    
    w = collection.getElementsByTagName("width")[0]
    w_val = int(w.firstChild.nodeValue)
    h = collection.getElementsByTagName("height")[0]
    h_val = int(h.firstChild.nodeValue)
    class_label = ""
    class_count = 0
    for object in objects:
        name = object.getElementsByTagName("name")[0].firstChild.nodeValue
        if name == class_i:
            class_count += 1
            xmin = object.getElementsByTagName("xmin")[0]
            xmin_val = int(xmin.firstChild.nodeValue)
            xmax = object.getElementsByTagName("xmax")[0]
            xmax_val = int(xmax.firstChild.nodeValue)
            ymin = object.getElementsByTagName("ymin")[0]
            ymin_val = int(ymin.firstChild.nodeValue)
            ymax = object.getElementsByTagName("ymax")[0]
            ymax_val = int(ymax.firstChild.nodeValue)
            
            # 0 for shift, 1 for resize
            operation = ("shift", "resize")
            operation_i = randint(0, 1)
            class_label += str(operation_i)
            factor = uniform(0.8, 1.2)
            if operation_i:
                class_box = resize(xmin_val, ymin_val, xmax_val, ymax_val, factor)
            else:
                class_box = shift(xmin_val, ymin_val, xmax_val, ymax_val, randint(0,1), factor)
            xmin.firstChild.replaceWholeText(str(class_box[0] if class_box[0] > 0 else 0))
            ymin.firstChild.replaceWholeText(str(class_box[1] if class_box[1] > 0 else 0))
            xmax.firstChild.replaceWholeText(str(class_box[2] if class_box[2] < w_val else w_val))
            ymax.firstChild.replaceWholeText(str(class_box[3] if class_box[3] < h_val else h_val))
        else:
            class_label += "-"
    
    # save only once for each 1216
    if class_count: 
        xml_name_new = os.path.splitext(xml_name)[0] + "_i" + class_label + "_" + str(randint(0, 99999999)).zfill(8) + ".xml"
        with open(xml_name_new, 'w') as newfile:
            DOMTree.writexml(newfile)
        jpg_name_new = os.path.splitext(xml_name_new)[0] + ".jpg"
        copy2(jpg_name, jpg_name_new)
            
    return class_count
    
 
def main(path, classes):
    """
        path: file path, augmented files will be generated onsite
        classes: {class_i:target} (note: this target number should exclude what we already have in this class)
    """
    xml_names = scan_files(path, postfix=".xml")
    shuffle(xml_names)
    for class_i, target in classes.items():
        count = 0
        while count < target:
            for xml_name in xml_names:
                count += process(xml_name, class_i)
                if count >= target:
                    break
       
       
if __name__ == "__main__":
    path = os.path.join(os.getcwd(), "train")
    classes = {"ASCUS":60000, "LSIL":50000, "ASCH":36000, "HSIL":100000, "SCC":36000}
    main(path, classes)
            