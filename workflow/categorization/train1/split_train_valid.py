import os
import random
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


def split_train_and_valid(data_path, save_path, split=0.1):
    def create_directory(save_path, classes):
        os.makedirs(os.path.join(save_path, "train"), exist_ok=True)
        for class_i in classes:
            os.makedirs(os.path.join(save_path, "valid", class_i), exist_ok=True)
    
    def remove_directory(data_path, subdirs):
        for subdir in subdirs:
            shutil.rmtree(os.path.join(data_path, subdir))
    
    subdirs = os.listdir(data_path)
    create_directory(save_path, subdirs)
    
    for subdir in subdirs:
        sub_path = os.path.join(data_path, subdir)
        sub_files = scan_files(sub_path)
        random.shuffle(sub_files)
        random.shuffle(sub_files)
        random.shuffle(sub_files)
                   
        sub_valid_path = os.path.join(save_path, "valid", subdir)
        sub_valid_files = sub_files[:int(len(sub_files)*split)]
        for file in sub_valid_files:
            shutil.move(file, sub_valid_path)
        
        train_path = os.path.join(save_path, "train")
        shutil.move(sub_path, train_path)
            
        print("{}: split # {} files to train, # {} files to valid".format(subdir, len(sub_files)-len(sub_valid_files), len(sub_valid_files)))
        
    # remove_directory(data_path, subdirs)


split = 0.1  # valid in all (train + valid)
data_path = "/home/hdd0/Develop/liyu/batch6.4-608-to-299/UP"

split_train_and_valid(data_path, data_path, split)

# for d in os.listdir(data_path):
#     print("processing", d)
#     data_path_i = os.path.join(data_path, d)
#     save_path_i = data_path_i
#     split_data_by_wsi(data_path_i, save_path_i, split)
#     print("finished", d)
