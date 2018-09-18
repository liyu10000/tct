# coding=utf-8
import os
import xml.dom.minidom

classes = {"ASCUS": [], "LSIL": [], "ASCH": [], "HSIL": [], "SCC": [], 
		   "AGC1": [], "AGC2": [], "ADC": [], "EC": [], "FUNGI": [],
           "TRI": [], "CC": [], "ACTINO": [], "VIRUS": [],
           "MC": [], "SC": [], "RC": [], "GEC": []}

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

def collect_labels_from_xml(xml_file):
    try:
        DOMTree = xml.dom.minidom.parse(xml_file)
    except:
        print("cannot open xml file")
        return
    collection = DOMTree.documentElement
    objects = collection.getElementsByTagName("object")
    for object in objects:
        name = object.getElementsByTagName("name")[0].firstChild.nodeValue
        xmin = int(object.getElementsByTagName("xmin")[0].firstChild.nodeValue)
        ymin = int(object.getElementsByTagName("ymin")[0].firstChild.nodeValue)
        xmax = int(object.getElementsByTagName("xmax")[0].firstChild.nodeValue)
        ymax = int(object.getElementsByTagName("ymax")[0].firstChild.nodeValue)
        classes[name].append((xmax-xmin, ymax-ymin))


if __name__ == "__main__":
	path = "C:\\Users\\liyud\\Desktop\\yantian_jpg\\2018-07-29-04_03_58_classify"
	xml_files = scan_files(path, postfix=".xml")
	for xml_file in xml_files:
		collect_labels_from_xml(xml_file)
	print(classes)