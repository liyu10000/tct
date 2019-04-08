import os
import shutil

from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed


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


def read_and_rename(txt_name, save_path):
    # if os.path.basename(txt_name).startswith('_'):
    #     return
    
    labels = set()
    with open(txt_name, 'r') as f:
        for line in f.readlines():
            tokens = line.strip().split()
            labels.add(tokens[0])
    
    img_name = os.path.splitext(txt_name)[0] + '.bmp'
    if len(labels) > 2:
        print("more than two labels:", txt_name)
    elif len(labels) == 0:
        print("no label:", txt_name)
        os.remove(txt_name)
        os.remove(img_name)
        return
    
    head = '_' + ''.join([l.zfill(2) for l in labels]) + '_'
    basename = os.path.splitext(os.path.basename(txt_name))[0]
    txt_name_new = os.path.join(save_path, head+basename+'.txt')
    shutil.move(txt_name, txt_name_new)
    img_name_new = os.path.join(save_path, head+basename+'.bmp')
    if os.path.isfile(img_name):
        shutil.move(img_name, img_name_new)


def batch_read_and_rename(txt_names, save_path):
    for txt_name in txt_names:
        read_and_rename(txt_name, save_path)


def worker(data_path, save_path):
    files = scan_files(data_path, postfix='.txt')
    print("# files:", len(files))
    
    os.makedirs(save_path, exist_ok=True)

    executor = ProcessPoolExecutor(max_workers=8)
    tasks = []

    batch_size = 10000
    for i in range(0, len(files), batch_size):
        batch = files[i : i+batch_size]
        # batch_read_and_rename(batch, save_path)
        tasks.append(executor.submit(batch_read_and_rename, batch, save_path))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))


if __name__ == "__main__":
    data_path = "/home/ssd_array/data/batch6.4_1216/rotate"
    save_path = "/home/ssd_array/data/batch6.4_1216/rotate_"
    
    worker(data_path, save_path)