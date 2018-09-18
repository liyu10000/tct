# coding=utf-8
import os
from xml.dom.minidom import parse
import xml.dom.minidom
from random import shuffle
from shutil import copy2


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


colors = {"MC":0, "SC":0, "RC":0, "GEC":0}

count = 0
def remove_normal(files_list):
    global count
    for xml_file in files_list:
        # open .xml file
        DOMTree = xml.dom.minidom.parse(xml_file)
        collection = DOMTree.documentElement
        objects = collection.getElementsByTagName("object")
        
        onlyThis = True
        for object in objects:
            name = object.getElementsByTagName("name")
            #print(name[0].firstChild.nodeValue)
            #if not name[0].firstChild.nodeValue in colors:
            if not name[0].firstChild.nodeValue in ["ASCUS", "ASCH"]:
                onlyThis = False
                
        if onlyThis:            
            os.remove(xml_file)
            jpg_file = os.path.splitext(xml_file)[0] + ".jpg"
            os.remove(jpg_file)
            # print(xml_file)
            # print(jpg_file)
            count += 1
            if (count == 3000):
                return

                
def remove_rotated(files):
    for file in files:
        file_pre = os.path.splitext(file)[0]
        file_jpg = file_pre + ".jpg"
        file_txt = file_pre + ".txt"
        if file_pre.endswith("_r90") or file_pre.endswith("_r180") or file_pre.endswith("_r270"):
        #if "shift" in file_pre or "resize" in file_pre:
            os.remove(file)
            os.remove(file_jpg)
            os.remove(file_txt)
            #os.remove(file_txt)
        # else:
            # os.rename(file, file.replace(" ", "-"))
            # os.rename(file_jpg, file_jpg.replace(" ", "-"))
            # os.rename(file_txt, file_txt.replace(" ", "-"))
            
    
def collect(files_list, save_path):
    for xml_file in files_list:
        # open .xml file
        DOMTree = xml.dom.minidom.parse(xml_file)
        collection = DOMTree.documentElement
        objects = collection.getElementsByTagName("object")
        
        hasThis = False
        for object in objects:
            name = object.getElementsByTagName("name")
            if name[0].firstChild.nodeValue in ["ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]:
                hasThis = True
                break
                
        if hasThis:
            copy2(xml_file, save_path)
            jpg_file = os.path.splitext(xml_file)[0] + ".jpg"
            copy2(jpg_file, save_path)
               
if __name__ == "__main__":
    path = os.path.join(os.getcwd(), "tct_data608_0716")
    files_list = scan_files(path, postfix=".xml")
    #shuffle(files_list)
    #remove_normal(files_list)
    save_path = os.path.join(os.getcwd(), "tct_data608_0716_5classes")
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    collect(files_list, save_path)
    #remove_rotated(files_list)



