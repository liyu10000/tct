import os
import csv
import xml.dom.minidom
import xml.etree.ElementTree as ET

def xception_convert(dict_pic_info, classes, img_size, save_path, det):
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
            if float(label_tokens[3]) > det:
                contains = True
                object = ET.SubElement(root, "object")
                ET.SubElement(object, "name").text = classes[int(label_tokens[2])]
                ET.SubElement(object, "pose").text = "Unspecified"
                ET.SubElement(object, "truncated").text = "0"
                ET.SubElement(object, "difficult").text = "0"
                bndbox = ET.SubElement(object, "bndbox")
                ET.SubElement(bndbox, "xmin").text = str(int(float(label_tokens[4])))
                ET.SubElement(bndbox, "ymin").text = str(int(float(label_tokens[5])))
                ET.SubElement(bndbox, "xmax").text = str(int(float(label_tokens[6])))
                ET.SubElement(bndbox, "ymax").text = str(int(float(label_tokens[7])))

        if contains:
            raw_string = ET.tostring(root, "utf-8")
            reparsed = xml.dom.minidom.parseString(raw_string)
            file = open(os.path.join(save_path, jpg + ".xml"), "w")
            file.write(reparsed.toprettyxml(indent="\t"))
            file.close()

def predictions_to_csv(dict_pic_info, classes_list, classes_all, csv_file):
    with open(csv_file, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["x_y", "segment", "det", "classify", "det", "xmin", "ymin", "xmax", "ymax"])
        for x_y, labels in dict_pic_info.items():
            for label in labels:
                label_tokens = label.split()
                writer.writerow([x_y, 
                                classes_list[int(label_tokens[0])], label_tokens[1], 
                                classes_all[int(label_tokens[2])], label_tokens[3], 
                                label_tokens[4], label_tokens[5], 
                                label_tokens[6], label_tokens[7]])
