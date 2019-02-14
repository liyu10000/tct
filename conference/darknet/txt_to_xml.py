import os
import xml.dom.minidom
import xml.etree.ElementTree as ET

from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed


# 13 classes, add SC and PH
classes = {"ACTINO":9, "AGC_A":0, "AGC_B":0, "ASCUS":4, "CC":6, "EC":3, "FUNGI":8, 
            "HSIL_B":1, "HSIL_M":1, "HSIL_S":1, "LSIL_E":5, "LSIL_F":5, "PH":11, 
            "SC":12, "SCC_G":1, "SCC_R":2, "TRI":10, "VIRUS":7}
classes = {0:"AGC", 1:"HSIL-SCC_G", 2:"SCC_R", 3:"EC", 4:"ASCUS", 5:"LSIL", 6:"CC", 
            7:"VIRUS", 8:"FUNGI", 9:"ACTINO", 10:"TRI", 11:"PH", 12:"SC"}


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


def read_txt(txt_name, size=608):
    labels = []
    with open(txt_name, 'r') as f:
        for line in f.readlines():
            tokens = line.strip().split()
            label = classes[int(tokens[0])]
            cx = float(tokens[1])
            cy = float(tokens[2])
            w = float(tokens[3])
            h = float(tokens[4])
            xmin = int((cx - w / 2) * size)
            ymin = int((cy - h / 2) * size)
            xmax = int((cx + w / 2) * size)
            ymax = int((cy + h / 2) * size)
            labels.append([label, xmin, ymin, xmax, ymax])
    return labels


def gen_xml(xml_name, labels):
    root = ET.Element("annotation")
    ET.SubElement(root, "folder").text = "folder"
    ET.SubElement(root, "filename").text = os.path.basename(os.path.splitext(xml_name)[0] + ".bmp")
    ET.SubElement(root, "path").text = "path"

    source = ET.SubElement(root, "source")
    ET.SubElement(source, "database").text = "Unknown"

    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = "608"
    ET.SubElement(size, "height").text = "608"
    ET.SubElement(size, "depth").text = "3"

    ET.SubElement(root, "segmented").text = "0"

    for labeli in labels:
        object = ET.SubElement(root, "object")
        ET.SubElement(object, "name").text = labeli[0]
        ET.SubElement(object, "pose").text = "Unspecified"
        ET.SubElement(object, "truncated").text = "0"
        ET.SubElement(object, "difficult").text = "0"
        bndbox = ET.SubElement(object, "bndbox")
        ET.SubElement(bndbox, "xmin").text = str(labeli[1])
        ET.SubElement(bndbox, "ymin").text = str(labeli[2])
        ET.SubElement(bndbox, "xmax").text = str(labeli[3])
        ET.SubElement(bndbox, "ymax").text = str(labeli[4])

    raw_string = ET.tostring(root, "utf-8")
    reparsed = xml.dom.minidom.parseString(raw_string)
    with open(xml_name, 'w') as f:
        f.write(reparsed.toprettyxml(indent="\t"))


def txt_to_xml(txt_name, save_path):
    labels = read_txt(txt_name)
    xml_name = os.path.basename(os.path.splitext(txt_name)[0] + ".xml")
    xml_name = os.path.join(save_path, xml_name)
    gen_xml(xml_name, labels)


def batch_txt_to_xml(txt_names, save_path):
    for txt_name in txt_names:
        txt_to_xml(txt_name, save_path)


def worker(data_path, save_path):
    files = scan_files(data_path, postfix=".txt")
    print("# files:", len(files))

    executor = ProcessPoolExecutor(max_workers=4)
    tasks = []

    batch_size = 10000
    for i in range(0, len(files), batch_size):
        batch = files[i : i+batch_size]
        # batch_txt_to_xml(batch)
        tasks.append(executor.submit(batch_txt_to_xml, batch, save_path))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))


if __name__ == "__main__":
    data_path = "/home/TMP4T/batch6.3-1216-yearend/original"
    save_path = data_path
    worker(data_path, save_path)