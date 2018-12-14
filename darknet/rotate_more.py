import os
import cv2
import numpy as np
from PIL import Image
import xml.dom.minidom
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed

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
    
def rotate(xml_name, img_path, img_save_path, postfix, degrees):
    basename = os.path.splitext(os.path.basename(xml_name))[0]
    img_prefix = os.path.join(img_save_path, basename)
    
    img = Image.open(os.path.join(img_path, basename+postfix))
    for degree in degrees:
        img.rotate(degree).save(img_prefix + "_" + str(degree) + postfix)
    img.close()
    
def rotate_cv2(xml_name, img_path, img_save_path, postfix, degrees):
    basename = os.path.splitext(os.path.basename(xml_name))[0]
    img_prefix = os.path.join(img_save_path, basename)
    
    img = cv2.imread(os.path.join(img_path, basename+postfix))
    for degree in degrees:
        img = np.rot90(img)
        img_out_path = img_prefix + "_" + str(degree) + postfix
        cv2.imwrite(img_out_path, img)

def gen_xml(xml_name, xml_save_path, degrees):
    DOMTree = xml.dom.minidom.parse(xml_name)
    collection = DOMTree.documentElement
    filename = collection.getElementsByTagName("filename")
    objects = collection.getElementsByTagName("object")
    
    w = collection.getElementsByTagName("width")[0]
    w_val = int(w.firstChild.nodeValue)
    h = collection.getElementsByTagName("height")[0]
    h_val = int(h.firstChild.nodeValue)
    
    xmins, ymins, xmaxs, ymaxs = [], [], [], []
    for object in objects:
        xmin = object.getElementsByTagName("xmin")[0]
        xmins.append(int(xmin.firstChild.nodeValue))
        xmax = object.getElementsByTagName("xmax")[0]
        xmaxs.append(int(xmax.firstChild.nodeValue))
        ymin = object.getElementsByTagName("ymin")[0]
        ymins.append(int(ymin.firstChild.nodeValue))
        ymax = object.getElementsByTagName("ymax")[0]
        ymaxs.append(int(ymax.firstChild.nodeValue))
    
    basename = os.path.splitext(os.path.basename(xml_name))[0]
    xml_prefix = os.path.join(xml_save_path, basename)
    
    # rotate 90
    if 90 in degrees:
        xml_name_new = xml_prefix + "_90.xml"
        filename[0].firstChild.replaceWholeText(os.path.basename(xml_name_new))
        i = 0
        for object in objects:
            xmin_val, ymin_val, xmax_val, ymax_val = xmins[i], ymins[i], xmaxs[i], ymaxs[i]
            i += 1
            xmin = object.getElementsByTagName("xmin")[0]
            xmax = object.getElementsByTagName("xmax")[0]
            ymin = object.getElementsByTagName("ymin")[0]
            ymax = object.getElementsByTagName("ymax")[0]
            xmin.firstChild.replaceWholeText(str(ymin_val))
            ymin.firstChild.replaceWholeText(str(w_val-xmax_val))
            xmax.firstChild.replaceWholeText(str(ymax_val))
            ymax.firstChild.replaceWholeText(str(w_val-xmin_val))    
        w.firstChild.replaceWholeText(str(h_val))
        h.firstChild.replaceWholeText(str(w_val))     
        with open(xml_name_new, 'w') as newfile:
            DOMTree.writexml(newfile)
        
    # rotate 180
    if 180 in degrees:
        xml_name_new = xml_prefix + "_180.xml"
        filename[0].firstChild.replaceWholeText(os.path.basename(xml_name_new))
        i = 0
        for object in objects:
            xmin_val, ymin_val, xmax_val, ymax_val = xmins[i], ymins[i], xmaxs[i], ymaxs[i]
            i += 1
            xmin = object.getElementsByTagName("xmin")[0]
            xmax = object.getElementsByTagName("xmax")[0]
            ymin = object.getElementsByTagName("ymin")[0]
            ymax = object.getElementsByTagName("ymax")[0]
            xmin.firstChild.replaceWholeText(str(w_val-xmax_val))
            ymin.firstChild.replaceWholeText(str(h_val-ymax_val))
            xmax.firstChild.replaceWholeText(str(w_val-xmin_val))
            ymax.firstChild.replaceWholeText(str(h_val-ymin_val))    
        w.firstChild.replaceWholeText(str(w_val))
        h.firstChild.replaceWholeText(str(h_val))     
        with open(xml_name_new, 'w') as newfile:
            DOMTree.writexml(newfile)
        
    # rotate 270
    if 270 in degrees:
        xml_name_new = xml_prefix + "_270.xml"
        filename[0].firstChild.replaceWholeText(os.path.basename(xml_name_new))
        i = 0
        for object in objects:
            xmin_val, ymin_val, xmax_val, ymax_val = xmins[i], ymins[i], xmaxs[i], ymaxs[i]
            i += 1
            xmin = object.getElementsByTagName("xmin")[0]
            xmax = object.getElementsByTagName("xmax")[0]
            ymin = object.getElementsByTagName("ymin")[0]
            ymax = object.getElementsByTagName("ymax")[0]
            xmin.firstChild.replaceWholeText(str(h_val-ymax_val))
            ymin.firstChild.replaceWholeText(str(xmin_val))
            xmax.firstChild.replaceWholeText(str(h_val-ymin_val))
            ymax.firstChild.replaceWholeText(str(xmax_val)) 
        w.firstChild.replaceWholeText(str(h_val))
        h.firstChild.replaceWholeText(str(w_val))        
        with open(xml_name_new, 'w') as newfile:
            DOMTree.writexml(newfile)

def batch_rotate(xml_names, img_path, img_save_path, xml_save_path, postfix, degrees):
    for xml_name in xml_names:
        # rotate_cv2(xml_name, img_path, img_save_path, postfix, degrees)
        gen_xml(xml_name, xml_save_path, degrees)
    
def do_rotate(xml_path, img_path, img_save_path, xml_save_path, postfix, degrees=[90]):
    xml_names = scan_files(xml_path, postfix=".xml")
    print("# files", len(xml_names))
    
    executor = ProcessPoolExecutor(max_workers=cpu_count()//3)
    tasks = []
    
    batch_size = 100
    for i in range(0, len(xml_names), batch_size):
        batch = xml_names[i : i+batch_size]
        tasks.append(executor.submit(batch_rotate, xml_names, img_path, img_save_path, xml_save_path, postfix, degrees))

    job_count = len(tasks)
    for future in as_completed(tasks):
        job_count -= 1
        print("One Job Done, Remaining Job Count: {}".format(job_count))
    
    
if __name__ == "__main__":
    # @do_rotate
    xml_path = "/home/ssd0/Develop/liyu/batch6_1216_labels/train"
    img_path = "/home/ssd0/Develop/liyu/batch6_1216/train"
    img_save_path = "/home/hdd_array0/batch_1216_rotate_c"
    xml_save_path = "/home/hdd_array0/batch_1216_rotate_c"
    postfix = ".bmp"
    degrees = [90, 180, 270]
    
    do_rotate(xml_path, img_path, img_save_path, xml_save_path, postfix, degrees)
    
#     # @single xml test
#     xml_name = "/home/ssd0/Develop/liyu/batch6_1216_labels/train/TC17042082_22180_42666.xml"
#     img_path = "/home/ssd0/Develop/liyu/batch6_1216/train"
#     img_save_path = "/home/hdd_array0/batch_1216_rotate"
#     xml_save_path = "/home/hdd_array0/batch_1216_rotate"
#     postfix = ".bmp"
#     degrees = [90, 180, 270]
    
#     rotate(xml_name, img_path, img_save_path, postfix, degrees)
#     gen_xml(xml_name, xml_save_path, degrees)
