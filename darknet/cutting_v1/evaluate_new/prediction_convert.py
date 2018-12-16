import os
import xml.dom.minidom
import xml.etree.ElementTree as ET
from prediction_evaluate import *

result_dir = "/home/sakulaki/code/yolo-pre-trained/darknet/results"
classes = ["ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]

dict_pic_info = get_predictions_result(result_dir, classes)

size = 608
sava_path = "/home/sakulaki/dataset/realtest/608/XB1800118"
for jpg, labels in dict_pic_info.items():
    root = ET.Element("annotation")
    ET.SubElement(root, "folder").text = "folder"
    ET.SubElement(root, "filename").text = jpg + ".jpg"
    ET.SubElement(root, "path").text = "path"

    source = ET.SubElement(root, "source")
    ET.SubElement(source, "database").text = "Unknown"

    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(size)
    ET.SubElement(size, "height").text = str(size)
    ET.SubElement(size, "depth").text = "3"

    ET.SubElement(root, "segmented").text = "0"
    
    for label in labels:
        label_tokens = label.split()
        object = ET.SubElement(root, "object")
        ET.SubElement(object, "name").text = classes[int(label_tokens[0])]
        ET.SubElement(object, "pose").text = "Unspecified"
        ET.SubElement(object, "truncated").text = "0"
        ET.SubElement(object, "difficult").text = "0"
        bndbox = ET.SubElement(object, "bndbox")
        ET.SubElement(bndbox, "xmin").text = str(int(float(label_tokens[2])))
        ET.SubElement(bndbox, "ymin").text = str(int(float(label_tokens[3])))
        ET.SubElement(bndbox, "xmax").text = str(int(float(label_tokens[4])))
        ET.SubElement(bndbox, "ymax").text = str(int(float(label_tokens[5])))

    raw_string = ET.tostring(root, "utf-8")
    reparsed = xml.dom.minidom.parseString(raw_string)
    file = open(os.path.join(save_path, jpg + ".xml"), "w")
    file.write(reparsed.toprettyxml(indent="\t"))
    file.close()