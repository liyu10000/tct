import os
import re
import csv
from random import shuffle
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

def select_same(files, factor, folder):
    shuffle(files)
    new_path = os.path.join(os.getcwd(), "valid/"+folder)
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    for i in range(int(len(files)*factor)):
        move(files[i], new_path)
    
def select_diff(files, factor, folder):
    tif_names = {}
    for file in files:
        file = os.path.basename(file)
        pattern = '201\d-\d\d-\d\d.{0,1}\d\d_\d\d_\d\d'
        tif_name = re.search(pattern, file).group()
        if not tif_name in tif_names:
            tif_names[tif_name] = 1
        else:
            tif_names[tif_name] += 1
    names = list(tif_names.keys())
    print(names)
    shuffle(names)
    new_path = os.path.join(os.getcwd(), "test/"+folder)
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    selected = []
    if len(names) < 5:
        return
    elif len(names) < 10:
        selected.append(names[0])
    else:
        for i in range(int(len(names)*factor)):
            selected.append(names[i])
    for i in selected:
        for file in files:
            if i in file:
                move(file, new_path)
                #move(os.path.splitext(file)[0]+".jpg", new_path)
    # train_path = os.path.join(os.getcwd(), "train")
    # if not os.path.exists(train_path):
        # os.makedirs(train_path)
    # for file in files:
        # if os.path.isfile(file):
            # move(file, train_path)
            # move(os.path.splitext(file)[0]+".jpg", train_path)

def count(path, upper_dirs, lower_dirs, out_csv):
    csv_file = open(out_csv, "w", newline='')
    writer = csv.writer(csv_file)
    writer.writerow([""]+lower_dirs)
    for upper_dir in upper_dir:
        upper_dir_count = [upper_dir,]
        for lower_dir in lower_dirs:
            path_i = os.path.join(path, upper_dir+"/"+lower_dir)
            files = scan_files(path_i, postfix=".jpg")
            upper_dir_count.append(len(files))
        writer.writerow(upper_dir_count)
    csv_file.close()

if __name__ == "__main__":
    folders = ["ACTINO", "ADC", "AGC1", "AGC2", "ASCH", "ASCUS", "CC", "EC", "FUNGI", "GEC", "HSIL", "LSIL", "MC", "RC", "SC", "SCC", "TRI", "VIRUS"]
    for folder in folders:
        path = os.path.join(os.getcwd(), "train/"+folder)
        files = scan_files(path, postfix=".jpg")
        #select_same(files, 0.1, folder)
    # classes = ["01_ASCUS", "02_LSIL", "03_ASCH", "04_HSIL", "05_SCC"]
    # for class_i in classes:
        # files = scan_files(os.path.join(path, class_i), postfix=".xml")
        # select_diff(files, 0.1) 
        