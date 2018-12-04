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


def copy_by_depth(file_in, path_out, depth):
    tokens = file_in.rsplit(os.sep, depth+1)
    file_out = os.path.join(path_out, *tokens[1:])
    # parent_dir = os.path.dirname(file_out)
    # os.makedirs(parent_dir, exist_ok=True)
    shutil.copy(file_in, file_out)
    
    
def batch_copy_by_depth(files_in, path_out, depth):
    for file_in in files_in:
        copy_by_depth(file_in, path_out, depth)
    
    
def main(path_in, path_out, depth):
    files_in = scan_files(path_in, postfix=".txt")
        
    executor = ProcessPoolExecutor(max_workers=cpu_count())
    tasks = []
    
    batch_size = 1000
    for i in range(0, len(files_in), batch_size):
        batch = files_in[i : i+batch_size]
        tasks.append(executor.submit(batch_copy_by_depth, batch, path_out, depth))

    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))
        
        
if __name__ == "__main__":
    path_in = "/home/cnn/Documents/batch6_1216/train_txts_b"
    path_out = "/home/cnn/Documents/batch6_1216/train_hls"
    depth = 0
    main(path_in, path_out, depth)