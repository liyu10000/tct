import os
import pickle
import openslide
from xml.dom.minidom import parse
import xml.dom.minidom
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed

from tslide.tslide import TSlide


# # new 11 classes
# classes = {"ACTINO", "CC", "VIRUS", "FUNGI", "TRI", "AGC_A", "AGC_B", 
#            "EC", "HSIL_B", "HSIL_M", "HSIL_S", "SCC_G", "ASCUS", "LSIL_F",
#            "LSIL_E", "SCC_R"}


# 5 misleading classes
classes = {"HSIL_B":[], "HSIL_M":[], "HSIL_S":[], "SCC_G":[], "SCC_R":[]}



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


# read from keyword "Type"
def get_xml(xml_file):
    DOMTree = xml.dom.minidom.parse(xml_file)
    collection = DOMTree.documentElement
    annotations = collection.getElementsByTagName("Annotation")


    for annotation in annotations:
        cell = annotation.getElementsByTagName("Cell")
        class_i = cell[0].getAttribute("Type")
        if class_i in classes:
            classes[class_i].append(xml_file)
            break


def main(xml_path, save_path):
    files = scan_files(xml_path, postfix=".xml")
    print("# files:", len(files))

    for xml_file in files:
        get_xml(xml_file)
    


if __name__ == "__main__":
    xml_path = ""
    save_path = ""

    main(xml_path, save_path)

    print(classes)

    with open("hsil_scc.pkl", 'wb') as f:
        pickle.dump(classes, f)