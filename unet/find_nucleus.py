# coding: utf-8

import os
import sys
import cv2
import numpy as np
from skimage.filters import threshold_otsu
from test_seg import seg_img_and_save


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


def hls_trans(image, l_scale=0.5, s_scale=1.5):
    # 图像归一化，且转换为浮点型
    hlsImg = image.astype(np.float32)
    hlsImg = hlsImg / 255.0
    # 颜色空间转换 BGR转为HLS
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_BGR2HLS)
    # 1.调整亮度, 2.将hlsCopy[:, :, 1]和hlsCopy[:, :, 2]中大于1的全部截取
    # hlsImg[:, :, 1] = (1.0 + HLS_L) * hlsImg[:, :, 1]
    hlsImg[:, :, 1] = l_scale * hlsImg[:, :, 1]
    hlsImg[:, :, 1][hlsImg[:, :, 1] > 1] = 1
    # 2.调整饱和度
    # hlsImg[:, :, 2] = (1.0 + HLS_S) * hlsImg[:, :, 2]
    hlsImg[:, :, 2] = s_scale * hlsImg[:, :, 2]
    hlsImg[:, :, 2][hlsImg[:, :, 2] > 1] = 1
    # HLS2BGR
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_HLS2BGR)
    # 转换为8位unsigned char
    hlsImg = hlsImg * 255
    image = hlsImg.astype(np.uint8)
    
    return image


def get_mask(file_name, save_path):
    img = cv2.imread(file_name)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = gray > threshold_otsu(gray)/1.35
    img2 = np.array(mask*255, dtype=np.uint8)

    img3, contours, hierarchy = cv2.findContours(img2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    area = 0.0
    gray_amount = 0.0

    try:
        # calculate gray "amount" in contour region
        mask_contour = np.zeros_like(gray)
        cv2.drawContours(mask_contour, contours, 1, color=255, thickness=-1)
        
        file_name_new = os.path.join(save_path, os.path.splitext(os.path.basename(file_name))[0]+".png")
        cv2.imwrite(file_name_new, mask_contour)

    except:
        print(file_name) # don't find more than one contour

    return area, gray_amount


def find_contour(file_name, save_path):
    img0 = cv2.imread(file_name)

    img = hls_trans(img0)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = gray > threshold_otsu(gray)/1.35
    img2 = np.array(mask*255, dtype=np.uint8)

    img3, contours, hierarchy = cv2.findContours(img2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    area = 0.0
    gray_amount = 0.0

    try:
        # find convex hull of contour
        hull = cv2.convexHull(contours[1], False)

        # draw contour and save image
        cv2.drawContours(img0, [hull], 0, (0,0,255), 1)
        file_name_new = os.path.join(save_path, os.path.basename(file_name))
        cv2.imwrite(file_name_new, img0)

        # calculate area of contour region
        area = cv2.contourArea(contours[1])

        # calculate gray "amount" in contour region
        mask_contour = np.zeros_like(gray)
        cv2.drawContours(mask_contour, contours, 1, color=255, thickness=-1)
        
        pts = np.where(mask_contour == 255)
        gray_contour = gray[pts[0], pts[1]]
        gray_amount = 255*len(gray_contour) - sum(gray_contour)

    except:
        print(file_name) # don't find more than one contour

    return area, gray_amount


def find_main(src_path, dst_path, postfix):
    print("processing", src_path)
    files = scan_files(src_path, postfix=postfix)
    print("# files", len(files))

    os.makedirs(dst_path, exist_ok=True)

    areas = []
    gray_amounts = []

    for i,file_name in enumerate(files):
        if i % 1000 == 0:
            print(i)
        area, gray_amount = find_contour(file_name, dst_path)
        if gray_amount > 0.0:
            areas.append(area)
            gray_amounts.append(gray_amount)

    print("area", sum(areas)/len(areas), "gray", sum(gray_amounts)/len(gray_amounts))


def calc_gray(file_name, mask_name):
    img = cv2.imread(file_name)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    mask = cv2.imread(mask_name)
    mask = mask[:, :, 0]

    area = cv2.countNonZero(mask)

    pts = np.where(mask == 255)
    gray_contour = gray[pts[0], pts[1]]
    gray_amount = 255*len(gray_contour) - sum(gray_contour)
    
    return area, gray_amount


def calc_main(file_path, mask_path, file_postfix=".bmp", mask_postfix=".png"):
    print("processing", file_path)
    file_names = scan_files(file_path, postfix=file_postfix)
    print("# files", len(file_names))

    areas = []
    gray_amounts = []

    f = open(os.path.join(file_path, "result.txt"), 'w')

    for file_name in file_names:
        mask_name = os.path.join(mask_path, os.path.splitext(os.path.basename(file_name))[0] + mask_postfix)
        if not os.path.isfile(mask_name):
            continue
        area, gray_amount = calc_gray(file_name, mask_name)
        areas.append(area)
        gray_amounts.append(gray_amount)

        f.write("{}: area {}, gray {}\n".format(os.path.basename(file_name), area, gray_amount))

    f.write("\narea {}, gray {}".format(sum(areas)/len(areas), sum(gray_amounts)/len(gray_amounts)))

    f.close()
    print("area", sum(areas)/len(areas), "gray", sum(gray_amounts)/len(gray_amounts))  



if __name__ == "__main__":
    # # @test find_main
    # src_path = "/media/lukawa/two_disk/SC_test/TC18008922/SC"
    # dst_path = "/media/lukawa/two_disk/SC_test/TC18008922/SC-2"
    # postfix = ".jpg"

    # find_main(src_path, dst_path, postfix)


    # @test seg_img_and_save
    # testdir = "/media/lukawa/two_disk/cells_dna_test/NJ18044903 假ASCUS/ASCUS"
    # savedir = "/media/lukawa/two_disk/cells_dna_test/NJ18044903 假ASCUS/ASCUS-unet"

    testdir = sys.argv[1]
    savedir = sys.argv[2]

    seg_img_and_save(testdir, savedir)

    # @test calc_main
    file_path = savedir
    mask_path = savedir
    
    calc_main(file_path, mask_path)