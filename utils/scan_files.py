# search the path and return a list of files in the directory, including sub directories
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


def copy_by_depth(file_in, path_out, depth):
    tokens = file_in.rsplit(os.sep, depth+1)
    file_out = os.path.join(path_out, *tokens[1:])
    parent_dir = os.path.dirname(file_out)
    os.makedirs(parent_dir, exist_ok=True)
    shutil.copy(file_in, file_out)


def move_by_depth(file_in, path_out, depth):
    tokens = file_in.rsplit(os.sep, depth+1)
    file_out = os.path.join(path_out, *tokens[1:])
    parent_dir = os.path.dirname(file_out)
    os.makedirs(parent_dir, exist_ok=True)
    shutil.move(file_in, file_out)


def worker(data_path, save_path, postfix, depth):
    files = scan_files(data_path, postfix=postfix)
    print("# files:", len(files))

    executor = ProcessPoolExecutor(max_workers=cpu_count())
    tasks = []

    batch_size = 100
    for i in range(0, len(files), batch_size):
        batch = files[i : i+batch_size]
        tasks.append(executor.submit(XXXX_batch_func, batch, depth, **args))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))


# save chosen to file
import pickle

with open("chosen.pkl", 'wb') as f:
    pickle.dump(chosen, f)


# open saved chosen file
with open("chosen.pkl", 'rb') as f:
    chosen_ = pickle.load(f)