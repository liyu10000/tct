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
    

def rotate(image, degree):
    if degree == 90:
        image = cv2.transpose(image)
        image = cv2.flip(image, flipCode=0)
    elif degree == 180:
        image = cv2.flip(image, flipCode=0)
        image = cv2.flip(image, flipCode=1)
    elif degree == 270:
        image = cv2.transpose(image)
        image = cv2.flip(image, flipCode=1)
    return image

    
def batch_rotate(image_names, save_path, depth):
    for image_name in image_names:
        tokens = image_name.rsplit(os.sep, depth+1)
        save_path_i = os.path.join(save_path, *tokens[1:-1])
        print(image_name, save_path_i)
        os.makedirs(os.path.dirname(save_path_i), exist_ok=True)
        basename, ext = os.path.splitext(tokens[-1])

        image = cv2.imread(image_name)
        
        image_90 = rotate(image, 90)
        cv2.imwrite(os.path.join(save_path_i, basename + "_90" + ext), image_90)

        image_180 = rotate(image, 180)
        cv2.imwrite(os.path.join(save_path_i, basename + "_180" + ext), image_180)

        image_270 = rotate(image, 270)
        cv2.imwrite(os.path.join(save_path_i, basename + "_270" + ext), image_270)
    

def do_rotate(image_path, save_path, depth):
    image_names = scan_files(image_path, postfix=".jpg")
    print("# files", len(image_names))

    # batch_rotate(image_names, save_path, depth)

    executor = ProcessPoolExecutor(max_workers=cpu_count()//2)
    tasks = []

    batch_size = 100
    for i in range(0, len(image_names), batch_size):
        batch = image_names[i : i+batch_size]
        tasks.append(executor.submit(batch_rotate, batch, save_path, depth))

    job_count = len(tasks)
    for future in as_completed(tasks):
        job_count -= 1
        print("One Job Done, last Job Count: {}".format(job_count))
    


if __name__ == "__main__":
    image_path = "/home/cnn/Documents/immune/train-data"
    save_path = "/home/cnn/Documents/immune/train-data"
    depth = 2

    do_rotate(image_path, save_path, depth)