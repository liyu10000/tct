# search the path and return a list of files in the directory, including sub directories
import os
import csv
from shutil import copy

def scan_files(directory, prefix=None, postfix=None):
    """ return: full path names """
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

def scan_subdirs(directory, prefix=None, postfix=None):
    """ return: names of subdirectories, no full path name """
    subdirs_list = []
    for name in os.listdir(directory):
        name_path = os.path.join(directory, name)
        if os.path.isdir(name_path):
            if postfix:
                if name_path.endswith(postfix):
                    subdirs_list.append(name)
            elif prefix:
                if name_path.startswith(prefix):
                    subdirs_list.append(name)
            else:
                subdirs_list.append(name)
    return subdirs_list

def get_unrunned_tif(src_dir, des_dir):
    """ get a tif from scr_dir, if it is not in des_dir """
    src_tifs = os.listdir(src_dir)
    des_tifs = os.listdir(des_dir)
    for src_tif in src_tifs:
        if (src_tif.endswith(".tif") or src_tif.endswith(".kfb")) and not os.path.splitext(src_tif)[0] in des_tifs:
            return src_tif
    return ""

def dict_to_csv(dict_, csv_fullname):
    """
        dict_: {key:value}
        csv_fullname: full path name of output csv file
        output: csv file with key, value in a row
    """
    with open(csv_fullname, "w") as csv_file:
        writer = csv.writer(csv_file)
        for key,value in dict_.items():
            writer.writerow([key, value])

def csv_to_dict(csv_fullname):
    """
        csv_fullname: full path name of output csv file
        return: {key:value}
    """
    with open(csv_fullname, "r") as csv_file:
        reader = csv.reader(csv_file)
        dict_ = dict(reader)
    return dict_