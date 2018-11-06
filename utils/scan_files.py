# search the path and return a list of files in the directory, including sub directories
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


def copy_by_depth(file_in, path_out, depth):
    tokens = file_in.rsplit(os.sep, depth+1)
    file_out = os.path.join(path_out, *tokens[1:])
    parent_dir = os.path.dirname(file_out)
    os.makedirs(parent_dir, exist_ok=True)
    shutil.copy(file_in, file_out)