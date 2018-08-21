import os
import cv2
from random import shuffle
from shutil import copy

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

def cut_and_pad(image_name, save_path, size):
	"""
	image_name: image full path name
	size: targe image size to save
	save_path: image save path
	"""
	def pad_center(img, size):
		h, w, _ = img.shape
		dh, dw = size-h, size-w
		top, bottom = dh//2, dh-dh//2
		left, right = dw//2, dw-dw//2
		img_new = cv2.copyMakeBorder(img, top=top, bottom=bottom, left=left, right=right, 
									 borderType=cv2.BORDER_CONSTANT, value=BLACK)
		return img_new

	def pad_top_left(img, size):
		h, w, _ = img.shape
		top, bottom = max(size-h, 0), 0
		left, right = max(size-w, 0), 0
		img_new = cv2.copyMakeBorder(img, top=top, bottom=bottom, left=left, right=right, 
									 borderType=cv2.BORDER_CONSTANT, value=BLACK)
		h_new, w_new, _ = img_new.shape
		return img_new[h_new-size:, w_new-size:]

	def pad_top_right(img, size):
		h, w, _ = img.shape
		top, bottom = max(size-h, 0), 0
		left, right = 0, max(size-w, 0)
		img_new = cv2.copyMakeBorder(img, top=top, bottom=bottom, left=left, right=right, 
									 borderType=cv2.BORDER_CONSTANT, value=BLACK)
		h_new, w_new, _ = img_new.shape
		return img_new[h_new-size:, :size]

	def pad_bottom_left(img, size):
		h, w, _ = img.shape
		top, bottom = 0, max(size-h, 0)
		left, right = max(size-w, 0), 0
		img_new = cv2.copyMakeBorder(img, top=top, bottom=bottom, left=left, right=right, 
									 borderType=cv2.BORDER_CONSTANT, value=BLACK)
		h_new, w_new, _ = img_new.shape
		return img_new[:size, w_new-size:]

	def pad_bottom_right(img, size):
		h, w, _ = img.shape
		top, bottom = 0, max(size-h, 0)
		left, right = 0, max(size-w, 0)
		img_new = cv2.copyMakeBorder(img, top=top, bottom=bottom, left=left, right=right, 
									 borderType=cv2.BORDER_CONSTANT, value=BLACK)
		h_new, w_new, _ = img_new.shape
		return img_new[:size, :size]

	img = cv2.imread(image_name)
	h, w, _ = img.shape
	basename = os.path.splitext(os.path.basename(image_name))[0]
	BLACK = (0, 0, 0)
	if max(h, w) < size:
		img_new = pad_center(img, size)
		cv2.imwrite(os.path.join(save_path, basename + "_0.jpg"), img_new)
	else:
		img_new = pad_top_left(img[:h//2, :w//2], size)
		cv2.imwrite(os.path.join(save_path, basename + "_1.jpg"), img_new)
		img_new = pad_top_right(img[:h//2, w//2:], size)
		cv2.imwrite(os.path.join(save_path, basename + "_2.jpg"), img_new)
		img_new = pad_bottom_left(img[h//2:, :w//2], size)
		cv2.imwrite(os.path.join(save_path, basename + "_3.jpg"), img_new)
		img_new = pad_bottom_right(img[h//2:, w//2:], size)
		cv2.imwrite(os.path.join(save_path, basename + "_4.jpg"), img_new)


def process(image_path, save_path, size, number):
	image_names = scan_files(image_path)
	shuffle(image_names)
	for i in range(number):
		if i >= len(image_names):
			break;
		cut_and_pad(image_names[i], save_path, size)

def select_split(src_path, factor, des1, des2):
	src_files = scan_files(src_path)
	shuffle(src_files)
	for i in range(int(len(src_files)*factor)):
		copy(src_files[i], des1)
	while i < len(src_files)-1:
		i += 1
		copy(src_files[i], des2)

if __name__ == "__main__":
	# input_path = "/home/sakulaki/yolo-yuli/xxx/tct_data_samesize_0718"
	# output_path = "/home/sakulaki/yolo-yuli/xxx/tct_data_samesize_0718_224"
	# for class_i in os.listdir(input_path):
	# 	output_path_i = os.path.join(output_path, class_i)
	# 	os.makedirs(output_path_i, exist_ok=True)
	# 	process(os.path.join(input_path, class_i), output_path_i, size=224, number=1000)
	# 	print("processed: ", class_i)

	src_path = "/home/sakulaki/yolo-yuli/xxx/tct_data_samesize_0718_224/all"
	des1 = "/home/sakulaki/yolo-yuli/xxx/tct_data_samesize_0718_224/train"
	des2 = "/home/sakulaki/yolo-yuli/xxx/tct_data_samesize_0718_224/valid"
	for class_i in os.listdir(src_path):
		src_i = os.path.join(src_path, class_i)
		des1_i = os.path.join(des1, class_i)
		os.makedirs(des1_i, exist_ok=True)
		des2_i = os.path.join(des2, class_i)
		os.makedirs(des2_i, exist_ok=True)
		select_split(src_i, 0.9, des1_i, des2_i)
		print("processed: ", class_i)

