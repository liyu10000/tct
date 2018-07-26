# search the path and return a list of files in the directory, including sub directories
import os
from shutil import copy

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

def scan_subdirs(directory, prefix=None, postfix=None):
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

def copy_files(src_path, des_path, postfix=None):
    files = scan_files(src_path, postfix)
    for file in files:
        copy(file, des_path)

def remove_files(src_path, postfix=None):
    files = scan_files(src_path, postfix)
    for file in files:
        os.remove(file)