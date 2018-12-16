import os
from PIL import Image, ImageEnhance
import xml.dom.minidom
from random import uniform
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
    
def brighten(xml_name):
    jpg_name_pre = os.path.splitext(xml_name)[0]
    jpg = Image.open(jpg_name_pre + ".jpg")
    factor = uniform(0.8, 1.2)
    jpg_name_new = jpg_name_pre + "_b" + str(factor)[:5] + ".jpg"
    ImageEnhance.Brightness(jpg).enhance(factor).save(jpg_name_new)
    jpg.close()
    xml_name_new = os.path.splitext(jpg_name_new)[0] + ".xml"
    copy2(xml_name, xml_name_new)
    
def main(path):
    xml_names = scan_files(path, postfix=".xml")
    for xml_name in xml_names:
        brighten(xml_name)
    
if __name__ == "__main__":
    #path = os.getcwd()
    path = os.path.join(os.getcwd(), "temp")
    main(path)