import os
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

def deep_copy(path_in, path_out, postfix=None):
    files = scan_files(path_in, postfix=postfix)
    length = len(path_in)
    for file in files:
        file_o = path_out + file[length:]
        parent_dir = os.path.dirname(file_o)
        os.makedirs(parent_dir, exist_ok=True)
        print(file_o + " copied")
        copy2(file, file_o)


if __name__ == "__main__":
    path_in = ""
    path_out = ""
    deep_copy(path_in, path_out, postfix=".xml")