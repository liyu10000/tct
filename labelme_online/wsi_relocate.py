import os
import shutil


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


xml_path = '/home/sakulaki/TCTDATA/stage2_labeled/labels/all'
wsi_path = '/home/sakulaki/TCTDATA/'

all_wsis = scan_files(wsi_path, postfix=".tif") + scan_files(wsi_path, postfix=".kfb")

count = 0
for xml in os.listdir(xml_path):
    for wsi in all_wsis:
        if xml in wsi:
            print(xml, wsi)
            count += 1
print(count)