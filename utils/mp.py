import os
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
    

def process(file, save_path):
    pass

    
def batch_process(files, save_path):
    for file in files:
        process(file, save_path)
    

def worker(data_path, save_path):
    files = scan_files(data_path, postfix=".txt")
    print("# files", len(files))

    executor = ProcessPoolExecutor(max_workers=cpu_count()//2)
    tasks = []

    batch_size = 10000
    for i in range(0, len(files), batch_size):
        batch = files[i : i+batch_size]
        tasks.append(executor.submit(batch_process, batch, save_path))

    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: {}".format(job_count))
    


if __name__ == "__main__":
    data_path = ""
    save_path = ""

    worker(data_path, save_path)