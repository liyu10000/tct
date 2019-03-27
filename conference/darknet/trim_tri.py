import os
import shutil
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed


classes = {10:[10,25]}

count = {key:0 for key in range(13)}


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


def rewrite(txt_name, save_path, size=608):
    lines_new = []
    changed = False
    with open(txt_name, 'r') as f:
        for line in f.readlines():
            tokens = line.strip().split()
            labeli = int(tokens[0])
            delete = False
            if labeli in classes:
                thres = classes[labeli]
                w, h = float(tokens[3])*size, float(tokens[4])*size
                if w < thres[0] or h < thres[0] or w > thres[1] or h > thres[1]:
                    changed = True
                    delete = True
            if delete is False:
                lines_new.append(line)
    
    if changed:
        if lines_new:
            with open(txt_name, 'w') as f:
                for line in lines_new:
                    f.write(line)
        else:
#             os.remove(txt_name)
#             img_name = os.path.splitext(txt_name)[0] + '.bmp'
#             if os.path.isfile(img_name):
#                 os.remove(img_name)
            shutil.move(txt_name, save_path)
            img_name = os.path.splitext(txt_name)[0] + '.bmp'
            shutil.move(img_name, save_path)


# def rewrite(txt_name, save_path, size=608):
#     is_in = False
#     with open(txt_name, 'r') as f:
#         for line in f.readlines():
#             tokens = line.strip().split()
#             labeli = int(tokens[0])
#             if labeli in classes:
#                 is_in = True
                
#     if is_in:
#         shutil.move(txt_name, save_path)
#         img_name = os.path.splitext(txt_name)[0] + '.bmp'
#         shutil.move(img_name, save_path)


# def rewrite(txt_name, save_path, size=608):
#     not_in = False
#     with open(txt_name, 'r') as f:
#         for line in f.readlines():
#             tokens = line.strip().split()
#             labeli = int(tokens[0])
#             if labeli not in classes:
#                 not_in = True
#     if not_in:
#         os.remove(txt_name)
#         img_name = os.path.splitext(txt_name)[0] + '.bmp'
#         if os.path.isfile(img_name):
#             os.remove(img_name)


def batch_rewrite(txt_names, save_path):
    for txt_name in txt_names:
        rewrite(txt_name, save_path)
        
        
def worker(data_path, save_path):
    files = scan_files(data_path, postfix='.txt')
    print("# files:", len(files))
    
    os.makedirs(save_path, exist_ok=True)

    executor = ProcessPoolExecutor(max_workers=4)
    tasks = []

    batch_size = 10000
    for i in range(0, len(files), batch_size):
        batch = files[i : i+batch_size]
        # batch_rewrite(batch, save_path)
        tasks.append(executor.submit(batch_rewrite, batch, save_path))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))
            
            
            
if __name__ == "__main__":
    data_path = "/home/ssd_array0/Data/batch6.4_1216/tri"
    save_path = "/home/ssd_array0/Data/batch6.4_1216/tri-delete"
    
    worker(data_path, save_path)

    
#     data_paths = ["/home/ssd_array0/Data/batch6.4_1216/original", 
#                   "/home/ssd_array0/Data/batch6.4_1216/original-added", 
#                   "/home/ssd_array0/Data/batch6.4_1216/rotate", 
#                   "/home/ssd_array0/Data/batch6.4_1216/rotate-added"]
#     save_path = "/home/ssd_array0/Data/batch6.4_1216/tri"
#     for data_path in data_paths:
#         worker(data_path, save_path)