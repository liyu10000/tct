import os
import xml.dom.minidom
import xml.etree.ElementTree as ET
from prediction_evaluate import *
from utils import csv_to_dict

# result_dir = "/home/sakulaki/code/yolo-pre-trained/darknet/results"
# classes = ["ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]
# dict_pic_info = get_predictions_result(result_dir, classes)

# img_size = 608
# save_path = "/home/sakulaki/dataset/realtest/608/XB1800118"

def prediction_convert(dict_pic_info, classes, img_size, save_path, det):
    os.makedirs(save_path, exist_ok=True)
    for jpg, labels in dict_pic_info.items():
        root = ET.Element("annotation")
        ET.SubElement(root, "folder").text = "folder"
        ET.SubElement(root, "filename").text = jpg + ".jpg"
        ET.SubElement(root, "path").text = "path"

        source = ET.SubElement(root, "source")
        ET.SubElement(source, "database").text = "Unknown"

        size = ET.SubElement(root, "size")
        ET.SubElement(size, "width").text = str(img_size)
        ET.SubElement(size, "height").text = str(img_size)
        ET.SubElement(size, "depth").text = "3"

        ET.SubElement(root, "segmented").text = "0"
        
        contains = False
        for label in labels:
            label_tokens = label.split()
            if float(label_tokens[1]) > det:
                contains = True
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

        if contains:
            raw_string = ET.tostring(root, "utf-8")
            reparsed = xml.dom.minidom.parseString(raw_string)
            file = open(os.path.join(save_path, jpg + ".xml"), "w")
            file.write(reparsed.toprettyxml(indent="\t"))
            file.close()

if __name__ == "__main__":
    # result_dir = "/home/sakulaki/code/yolo-pre-trained/darknet/results"
    # classes_list = ["ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]
    # dict_pic_info = get_predictions_result(result_dir, classes_list)
    # img_size = 608
    # save_path = "/home/sakulaki/dataset/realtest/608/XB1800118"
    # det = 0.3
    # prediction_convert(dict_pic_info, classes_list, img_size, save_path, det)

    csv_file = "D:/2018-08-13-test_jpg/2018-08-13-14_15_41/2018-08-13-14_15_41_s.csv"
    dict_ = csv_to_dict(csv_file)
    classes = ["ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]
    img_size = 608
    save_path = "D:/2018-08-13-test_jpg/2018-08-13-14_15_41/xmls"
    det = 0.9
    prediction_convert(dict_, classes, img_size, save_path, det)