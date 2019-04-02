import os
import cv2
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


def vh_flip(image_name, data_path, save_path):
    pre = os.path.basename(image_name)
    
    image = None
    for path in data_path:
        if os.path.isfile(os.path.join(path, pre+'.bmp')):
            image = cv2.imread(os.path.join(path, pre+'.bmp'))
    if image is None:
        print('empty file', image_name)
        return
    v_img = cv2.flip(image, 0)
    h_img = cv2.flip(image, 1)
    
    v_img_name = os.path.join(save_path, pre+'_v.bmp')
    cv2.imwrite(v_img_name, v_img)
    
    h_img_name = os.path.join(save_path, pre+'_h.bmp')
    cv2.imwrite(h_img_name, h_img)
    
    
def batch_vh_flip(image_names, data_path, save_path):
    for image_name in image_names:
        vh_flip(image_name, data_path, save_path)


def worker(data_path, save_path):
    files = scan_files(save_path, postfix=".txt")
    files = [f.rsplit('_', 1)[0] for f in files]
    files = list(set(files))
    print("# files:", len(files))

    executor = ProcessPoolExecutor(max_workers=4)
    tasks = []

    batch_size = 10000
    for i in range(0, len(files), batch_size):
        batch = files[i : i+batch_size]
        tasks.append(executor.submit(batch_vh_flip, batch, data_path, save_path))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))
        
        
if __name__ == "__main__":
    data_path = ["/home/ssd_array0/Data/batch6.4_1216/ascus"]
    save_path = "/home/ssd_array0/Data/batch6.4_1216/ascus-flip"

    worker(data_path, save_path)
    
#     data_path = ["/home/ssd_array0/Data/batch6.4_1216/original", 
#                  "/home/ssd_array0/Data/batch6.4_1216/original-added", 
#                  "/home/ssd_array0/Data/batch6.4_1216/rotate", 
#                  "/home/ssd_array0/Data/batch6.4_1216/rotate-added"]
#     save_path = "/home/ssd_array0/Data/batch6.4_1216/flip"
#     worker(data_path, save_path)