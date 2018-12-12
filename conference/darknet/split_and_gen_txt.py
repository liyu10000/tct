import os
import random


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


def generate_txt(data_path, split=0.1):
    jpg_names = scan_files(data_path, postfix=".bmp")
    print("# total:", len(jpg_names))
    
    random.shuffle(jpg_names)
    random.shuffle(jpg_names)
    random.shuffle(jpg_names)
    
    train_jpg_names = jpg_names[int(len(jpg_names)*split):]
    valid_jpg_names = jpg_names[:int(len(jpg_names)*split)]
    
    train_txt_name = os.path.join(os.path.dirname(data_path), "train.txt")
    valid_txt_name = os.path.join(os.path.dirname(data_path), "valid.txt")
                                  
    with open(train_txt_name, 'w') as f:
        for jpg_name in train_jpg_names:
            f.write(jpg_name + '\n')
    print("# train:", len(train_jpg_names))
                                  
    with open(valid_txt_name, 'w') as f:
        for jpg_name in valid_jpg_names:
            f.write(jpg_name + '\n')
    print("# valid:", len(valid_jpg_names))
                                  
                                  
if __name__ == "__main__":
    data_path = "/home/ssd0/Develop/liyu/batch6_hls09_1216/train"
    generate_txt(data_path)