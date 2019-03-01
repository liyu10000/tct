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

def deep_copy(filenames, path_out):
    # copy file to a different folder, with the same file tree
    for filename in filenames:
        tif_filename = os.path.splitext(os.path.join(path_out, os.path.basename(filename)))[0] + ".tif"
        if os.path.isfile(tif_filename):
            copy2(filename, os.path.join(path_out, os.path.basename(filename)))
        # copy2(filename, os.path.join(path_out, os.path.basename(filename)))
        # os.remove(filename)

if __name__ == "__main__":
    path_in = "E:\\data\\xml_backup_new"
    path_out = "E:\\data\\asap_all"
    # path_in = "/media/tsimage/Elements/data/labelimg_to_asap"
    # path_out = "/media/tsimage/Elements/data"
    classes = ("01_ASCUS", "02_LSIL", "03_ASCH", "04_HSIL", "05_SCC", "06_AGC1", "07_AGC2", "08_ADC", "09_EC", "10_FUNGI", "11_TRI", "12_CC", "13_ACTINO", "14_VIRUS")
    
    for class_i in classes:
        filenames = scan_files(os.path.join(path_in, class_i), postfix=".xml")
        print("total of " + str(len(filenames)) + " filenames found")
        path_out_i = os.path.join(path_out, class_i)
        if not os.path.exists(path_out_i):
            os.makedirs(path_out_i)
        deep_copy(filenames, path_out_i)
