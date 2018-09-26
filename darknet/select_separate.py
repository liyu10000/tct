import os
import re
import csv
from random import sample
from shutil import move

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

def _split_test_from_train(path_train, factor, path_test):
    files = scan_files(path_train, postfix=".xml")
    tif_names = set()
    pattern1 = re.compile("201\d-\d\d-\d\d.{0,1}\d\d_\d\d_\d\d")
    pattern2 = re.compile("[a-zA-Z]*[0-9]{6,}")
    for file in files:
        file = os.path.basename(file)
        m1 = pattern1.search(file)
        m2 = pattern2.search(file)
        if m1:
            tif_name = m1.group(0)
        elif m2:
            tif_name = m2.group(0)
        else:
            print("cannot match tif/kfb name")
            continue
        tif_names.add(tif_name)
    names = list(tif_names)
    os.makedirs(path_test, exist_ok=True)
    selected = sample(names, int(len(files)*factor))
    for i in selected:
        for file in files:
            if i in file:
                move(file, path_test)
                move(os.path.splitext(file)[0]+".jpg", path_test)

def split_test_from_train(path_train, factor=0.1):
    path_test = os.path.join(os.path.dirname(path_train), "test")
    folders = os.listdir(path_train)
    for folder in folders:
        _split_test_from_train(os.path.join(path_train, folder), factor, os.path.join(path_test, folder))


def _split_valid_from_train(path_train, factor, path_valid):
    os.makedirs(path_valid, exist_ok=True)
    files = scan_files(path_train, postfix=".xml")
    to_valid = sample(files, int(len(files)*factor))
    for file in to_valid:
        move(file, path_valid)
        move(os.path.splitext(file)[0]+".jpg", path_valid)

def split_valid_from_train(path_train, factor=0.1):
    path_valid = os.path.join(os.path.dirname(path_train), "valid")
    folders = os.listdir(path_train)
    for folder in folders:
        _split_valid_from_train(os.path.join(path_train, folder), factor, os.path.join(path_valid, folder))


if __name__ == "__main__":
    path_train = "/home/tsimage/tct_data_for_darknet/train"
    # split_test_from_train(path_train)
    split_valid_from_train(path_train)