# coding=utf-8

import os

from xml.dom.minidom import parse
import xml.dom.minidom


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


total = 0
def count(files_list):
    global total  # number of files
    for file in files_list:
        DOMTree = xml.dom.minidom.parse(file)
        collection = DOMTree.documentElement
        total += 1
        annotations = collection.getElementsByTagName("Annotation")

        for annotation in annotations:
            if annotation.getAttribute("Color") == "#F4FA58":  # wrong color (defalt: #F4FA58)
                annotation.setAttribute("Color", "#00aa7f")  # color to be changed to
                # print(annotation.getAttribute("Color"))
                # annotation.attributes["Color"].value.replace("#F4FA58", "#0055ff")

        with open(file, 'w') as newfile:
            DOMTree.writexml(newfile)
        # with open(file, 'w') as newfile:
        #     newfile.write(DOMTree.toxml())


file_path = "F:\\data0\\2018-05-08\\2018-05-08-dichong"
files_list = scan_files(file_path, postfix=".xml")
count(files_list)

print(total)

