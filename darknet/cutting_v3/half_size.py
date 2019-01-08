import os
import cv2


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


def half_size(filename, save_path):
    img = cv2.imread(filename)
    h, w, _ = img.shape
    half = img[h//4:h//4*3, w//4:w//4*3, :]
    save_name = os.path.join(save_path, os.path.basename(filename))
    cv2.imwrite(save_name, half)


def main(file_path, save_path):
    filenames = scan_files(file_path, postfix=".bmp")
    print("# files", len(filenames))

    os.makedirs(save_path, exist_ok=True)

    for filename in filenames:
        half_size(filename, save_path)


if __name__ == "__main__":
    file_path = "/home/nvme/CELLS/ASCUS"
    save_path = "/home/nvme/CELLS/ASCUS-half"

    main(file_path, save_path)