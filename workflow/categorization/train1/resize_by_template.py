import os
import cv2
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


def form_template(files, directories):
    template = {d:set() for d in directories}
    for file in files:
        directory = os.path.basename(os.path.dirname(file))
        basename = os.path.splitext(os.path.basename(file))[0]
        template[directory].add(basename)
        
    return template


def copy_by_template(files, template, save_path):
    for file in files:
        basename = os.path.splitext(os.path.basename(file))[0]
        for directory in template:
            if basename in template[directory]:
                shutil.move(file, os.path.join(save_path, directory))
                
                
def resize_by_template(files, template, save_path, size=299):
    for file in files:
        basename = os.path.splitext(os.path.basename(file))[0]
        for directory in template:
            if basename in template[directory]:               
                img = cv2.imread(file)
                img = cv2.resize(img, (size, size))
                img_name_new = os.path.join(save_path, directory, os.path.basename(file))
                cv2.imwrite(img_name_new, img)

def get_directories(data_path):
    directories = os.listdir(data_path)
    return directories


def create_directories(data_path, directories):
    for directory in directories:
        os.makedirs(os.path.join(data_path, directory), exist_ok=True)
                        
        
def worker(data_path, save_path, temp_path):   
    directories = get_directories(temp_path)
    print("target directories", directories)
    
    temp_files = scan_files(temp_path)
    template = form_template(temp_files, directories)
    print("finished forming template, # files: {}, # directories: {}".format(len(temp_files), len(template)))
    
    create_directories(save_path, directories)

    files = scan_files(data_path, postfix=".bmp")
    print("# files:", len(files))
    
    executor = ProcessPoolExecutor(max_workers=8)
    tasks = []

    batch_size = 10000
    for i in range(0, len(files), batch_size):
        batch = files[i : i+batch_size]
        tasks.append(executor.submit(resize_by_template, batch, template, save_path))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count)) 
        
        
if __name__ == "__main__":
    data_path = "/home/hdd0/Develop/liyu/batch6.4/hls09"
    save_path = "/home/hdd0/Develop/liyu/batch6.4-608-to-299/hls09"
    temp_path = "/home/hdd0/Develop/liyu/batch6.4-608-to-299/original"
    
    worker(data_path, save_path, temp_path)