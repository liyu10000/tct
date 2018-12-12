# coding=utf-8
import os
from xml.dom.minidom import parse
import xml.dom.minidom
from utils.scan_files import scan_files


def parse_path(files_list, offset):
    files_dic = {}
    # file = chenlijie_LSIL-chenlijie-0320_2017-10-10 14_56_09_Annotation 3.jpeg
    for file in files_list:
        file = file[offset+1:]  # no overhead
        # file = file[offset+7:]  # depends on the overhead of file name
        file = file.rsplit(".", 1)[0]  # chenlijie_LSIL-chenlijie-0320_2017-10-10 14_56_09_Annotation 3
        prev, anno_i = file.rsplit("_", 1)
        filename = prev[len(prev)-19:]  # 2017-10-10 14_56_09
        prev = prev[:len(prev)-20]  # chenlijie_LSIL-chenlijie-0320
        prev_tokens = prev.split("_")

        path = ""

        for token in prev_tokens:
            path += token + "\\"
        # path += prev_tokens[0] + "_" + prev_tokens[1] + "\\"
        # for i in range(2, len(prev_tokens)):
        #     path += prev_tokens[i] + "\\"

        path += filename
        path += ".xml"

        if path in files_dic:
            files_dic[path].append(anno_i)
        else:
            files_dic[path] = [anno_i,]

    return files_dic


def batch_delete(files_dic, target_path):
    for file, annos in files_dic.items():
        delete(target_path + "\\" + file, annos)


def delete(file, annos):
    try:
        DOMTree = xml.dom.minidom.parse(file)
    except:
        print(file + " does not exist")
        return
    collection = DOMTree.documentElement
    annotations = collection.getElementsByTagName("Annotation")

    for annotation in annotations:
        if annotation.getAttribute("Name") in annos:  # annotation to delete
            parent = annotation.parentNode
            parent.removeChild(annotation)

    with open(file, 'w') as newfile:
        DOMTree.writexml(newfile)


def batch_change(files_dic, target_path, color):
    for file, annos in files_dic.items():
        change(target_path + "\\" + file, annos, color)


def change(file, annos, color):
    try:
        DOMTree = xml.dom.minidom.parse(file)
        collection = DOMTree.documentElement
        annotations = collection.getElementsByTagName("Annotation")

        for annotation in annotations:
            if annotation.getAttribute("Name") in annos:  # annotation to change color
                annotation.setAttribute("Color", color)  # color to be changed to
                # print(annotation.getAttribute("Color"))
                # annotation.attributes["Color"].value.replace("#F4FA58", "#0055ff")

        with open(file, 'w') as newfile:
            DOMTree.writexml(newfile)

    except:
        print(file + " cannot be processed")


def delete_dots(file):
    DOMTree = xml.dom.minidom.parse(file)
    collection = DOMTree.documentElement
    annotations = collection.getElementsByTagName("Annotation")

    for annotation in annotations:
        coordinates = annotation.getElementsByTagName("Coordinate")
        if len(coordinates) < 3:
            parent = annotation.parentNode
            parent.removeChild(annotation)

    with open(file, 'w') as newfile:
        DOMTree.writexml(newfile)


def batch_delete_dots(file_path):
    file_list = scan_files(file_path, postfix=".xml")
    for file in file_list:
        delete_dots(file)


if __name__ == "__main__":
    # the file path that contains the images to delete or change
    file_path = "D:\\data0\\2018-05-05-AGC+VIRUS\\2018-05-05-VIRUS-shenhe\\shandiaode"
    files_list = scan_files(file_path, postfix=".jpg")

    # the file path that contains xml files
    target_path = "D:\\"

    files_dic = parse_path(files_list, len(file_path))

    # delete annotations
    batch_delete(files_dic, target_path)

    # # change annotations
    # batch_change(files_dic, target_path, "#aa0000")

    # # delete single dots in xml
    # file_path = "D:\\data7\\15_special"
    # batch_delete_dots(file_path)
