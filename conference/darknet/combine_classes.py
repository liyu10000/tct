""" combine classes to one class, for yolo training
"""

import os
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed


# source classes in yolo txts
classes = {"ASCUS":0, "LSIL":1, "ASCH":2, "HSIL":3, "SCC":4, "AGC":5, 
           "EC":6, "FUNGI":7, "TRI":8, "CC":9, "ACTINO":10, "VIRUS":11}
# target classes to change to 
targets = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0}

count = {value:0 for key,value in classes.items()}

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


def change_txt(txt_name, save_path):
    labels = []
    with open(txt_name, 'r') as f:
        for line in f.readlines():
            tokens = line.strip().split()
            count[int(tokens[0])] += 1
            labels.append(tokens)
                      
    txt_name_new = os.path.join(save_path, os.path.basename(txt_name))
    with open(txt_name_new, 'w') as f:
        for tokens in labels:
            tokens[0] = str(targets[int(tokens[0])])
            f.write(' '.join(tokens) + '\n')

                      
def batch_change_txt(txt_names, save_path):
    for txt_name in txt_names:
        change_txt(txt_name, save_path)
                      
                      
def main(txt_path, save_path):
    txt_names = scan_files(txt_path, postfix=".txt")
    print("# of files: {}".format(len(txt_names)))
                      
    executor = ProcessPoolExecutor(max_workers=cpu_count())
    tasks = []
                      
    batch_size = 1000
    for i in range(0, len(txt_names), batch_size):
        batch = txt_names[i : i+batch_size]
        tasks.append(executor.submit(batch_change_txt, batch, save_path))    
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))
                      
                    
if __name__ == "__main__":
    txt_path = "/home/cnn/Documents/batch6_1216/train_txts"
    save_path = "/home/cnn/Documents/batch6_1216/train_txts_b"
    main(txt_path, save_path)
    print(count)
                      
            