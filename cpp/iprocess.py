import os
import cv2
import numpy as np
from datetime import datetime


def hls_trans(image):
    hlsImg = image.astype(np.float32)
    hlsImg = hlsImg / 255.0
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_BGR2HLS)
    hlsImg[:, :, 2] = 1.5 * hlsImg[:, :, 2]
    hlsImg[:, :, 2][hlsImg[:, :, 2] > 1] = 1
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_HLS2BGR)
    hlsImg = hlsImg * 255
    image = hlsImg.astype(np.uint8)
    return image

# wrong approach
def hls_trans_RGB(image):
    hlsImg = image.astype(np.float32)
    hlsImg = hlsImg / 255.0
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_RGB2HLS)
    hlsImg[:, :, 2] = 1.5 * hlsImg[:, :, 2]
    hlsImg[:, :, 2][hlsImg[:, :, 2] > 1] = 1
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_HLS2RGB)
    hlsImg = hlsImg * 255
    image = hlsImg.astype(np.uint8)
    return image


def hls_trans_(image):
    hlsImg = image.astype(np.float32)
    hlsImg = hlsImg / 255.0
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_BGR2HLS)
    hlsImg[:, :, 2] = 1.5 * hlsImg[:, :, 2]
    # hlsImg[:, :, 2][hlsImg[:, :, 2] > 1] = 1
    _, hlsImg[:, :, 2] = cv2.threshold(hlsImg[:, :, 2], 1, 1, cv2.THRESH_TRUNC)
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_HLS2BGR)
    hlsImg = hlsImg * 255
    image = hlsImg.astype(np.uint8)
    return image


def process(image):
    image = hls_trans(image)
    image = cv2.medianBlur(image, 5)
    image = cv2.GaussianBlur(image, (3,3), 1)
    return image


if __name__ == "__main__":
    a = 'test.bmp'
    img = cv2.imread(a)

    # time1 = datetime.now()
    # for i in range(1000):
    #     i1 = hls_trans(img)
    # time2 = datetime.now()
    # print(time2 - time1)

    # time1 = datetime.now()
    # for i in range(1000):
    #     i2 = hls_trans_(img)
    # time2 = datetime.now()
    # print(time2 - time1)


    # i1 = process(img)
    # cv2.imwrite('test-py1.bmp', i1)

    # i2 = hls_trans_RGB(img)
    # cv2.imwrite('test-py1-rgb.bmp', i2)


    a = 'test-c.bmp'
    b = 'test-py1.bmp'
    i1 = cv2.imread(a)
    i2 = cv2.imread(b)


    count = 0
    h, w, c = i1.shape
    for i in range(h):
        for j in range(w):
            for k in range(c):
                if abs(i1[i][j][k] - i2[i][j][k]) > 0:
                    count += 1
                    print(i1[i][j][k], i2[i][j][k])
    print(count)