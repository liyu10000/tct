import os
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
    
def select(files, factor):
    tif_names = {}
    for file in files:
        file = os.path.basename(file)
        if not file[:19] in tif_names:
            tif_names[file[:19]] = 1
        else:
            tif_names[file[:19]] += 1
    names = list(tif_names.keys())
    print(names)
    print()
    shuffle(names)
    valid_path = os.path.join(os.getcwd(), "test")
    if not os.path.exists(valid_path):
        os.makedirs(valid_path)
    selected = []
    if len(names) < 10:
        selected.append(names[0])
    else:
        for i in range(int(len(names)*factor)):
            selected.append(names[i])
    for i in selected:
        for file in files:
            if i in file:
                move(file, valid_path)
                move(os.path.splitext(file)[0]+".jpg", valid_path)
    # train_path = os.path.join(os.getcwd(), "train")
    # if not os.path.exists(train_path):
        # os.makedirs(train_path)
    # for file in files:
        # if os.path.isfile(file):
            # move(file, train_path)
            # move(os.path.splitext(file)[0]+".jpg", train_path)
    
if __name__ == "__main__":
    path = os.path.join(os.getcwd(), "train")
    files = scan_files(path, postfix=".xml")
    select(files, 0.1)
    # classes = ["01_ASCUS", "02_LSIL", "03_ASCH", "04_HSIL", "05_SCC"]
    # for class_i in classes:
        # files = scan_files(os.path.join(path, class_i), postfix=".xml")
        # select(files, 0.1) 
        