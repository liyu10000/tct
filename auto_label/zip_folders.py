import os

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

folder_names = scan_subdirs(os.getcwd(), postfix="_classify")
for folder_name in folder_names:
    os.system("zip -r {} {}".format(folder_name, os.path.join(os.getcwd(), folder_name)))
