import os
import cv2
import numpy as np


HLS_L = 0.20
HLS_S = 0.8


def hls_trans(image_name):
    image = cv2.imread(image_name)

    # 图像归一化，且转换为浮点型
    hlsImg = image.astype(np.float32)
    hlsImg = hlsImg / 255.0
    # 颜色空间转换 BGR转为HLS
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_BGR2HLS)
    # 1.调整亮度, 2.将hlsCopy[:, :, 1]和hlsCopy[:, :, 2]中大于1的全部截取
    hlsImg[:, :, 1] = (1.0 + HLS_L) * hlsImg[:, :, 1]
    hlsImg[:, :, 1][hlsImg[:, :, 1] > 1] = 1
    # 2.调整饱和度
    hlsImg[:, :, 2] = (1.0 + HLS_S) * hlsImg[:, :, 2]
    hlsImg[:, :, 2][hlsImg[:, :, 2] > 1] = 1
    # HLS2BGR
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_HLS2BGR)
    # 转换为8位unsigned char
    hlsImg = hlsImg * 255
    image = hlsImg.astype(np.uint8)
    
    cv2.imwrite(os.path.join(save_path, os.path.basename(image_name)), image)


if __name__ == "__main__":
    image_name = ""
    save_path = ""
    hls_trans(image_name, save_path)