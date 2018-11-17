import os
from PIL import Image
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


def resize_img_with_padding(img, size):
    img_croped = img.crop(
        (
            -((size - img.size[0]) / 2),
            -((size - img.size[1]) / 2),
            img.size[0] + (size - img.size[0]) / 2,
            img.size[1] + (size - img.size[1]) / 2
        )
    )
    img_resized = img_croped.resize((size, size))
    return img_resized


def resize_img_with_padding_full(image_name, depth, save_path, size):
    img = Image.open(image_name)
    img_resized = resize_img_with_padding(img, size)
    tokens = image_name.rsplit(os.sep, depth+1)
    image_name_out = os.path.join(save_path, *tokens[1:])
    os.makedirs(os.path.dirname(image_name_out), exist_ok=True)
    img_resized.save(image_name_out)


def batch_resize_img_with_padding_full(image_names, depth, save_path, size):
    for image_name in image_names:
        resize_img_with_padding_full(image_name, depth, save_path, size)


def process(image_path, depth, save_path, size=299):
    image_names = scan_files(image_path, postfix=".jpg")
    print("total of {} images to process".format(len(image_names)))

    executor = ProcessPoolExecutor(max_workers=cpu_count() - 2)
    tasks = []

    batch_size = 1000
    for i in range(0, len(image_names), batch_size):
        batch = image_names[i : i+batch_size]
        tasks.append(executor.submit(batch_resize_img_with_padding_full, batch, depth, save_path, size))

    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: {}".format(job_count))


if __name__ == "__main__":
    image_path = "/home/nvme/CELLS_hls"
    depth = 1
    save_path = "/home/nvme/CELLS_hls_299"
    size = 299
    process(image_path, depth, save_path, size)