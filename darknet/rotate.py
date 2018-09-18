import os
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
    
def rotate(xml_name):
    jpg_name_pre = os.path.splitext(xml_name)[0]
    jpg = Image.open(jpg_name_pre + ".jpg")
    jpg.rotate(90).save(jpg_name_pre + "_r90.jpg")
    jpg.rotate(180).save(jpg_name_pre + "_r180.jpg")
    jpg.rotate(270).save(jpg_name_pre + "_r270.jpg")
    jpg.close()

def gen_xml(xml_name):
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
        
    # rotate 90
    xml_name_new = os.path.splitext(xml_name)[0] + "_r90.xml"
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
    xml_name_new = os.path.splitext(xml_name)[0] + "_r180.xml"
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
    xml_name_new = os.path.splitext(xml_name)[0] + "_r270.xml"
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
    

def do_rotate(path):
    xml_names = scan_files(path, postfix=".xml")
    executor = ProcessPoolExecutor(max_workers=cpu_count() - 4)
    tasks = []
    for xml_name in xml_names:
        tasks.append(executor.submit(rotate, xml_name))
        tasks.append(executor.submit(gen_xml, xml_name))

    job_count = len(tasks)
    for future in as_completed(tasks):
        job_count -= 1
        print("One Job Done, last Job Count: {}".format(job_count))
    
if __name__ == "__main__":
    path = ""
    do_rotate(path)