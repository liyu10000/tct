from __future__ import division

from staintools import ReinhardNormalizer
from staintools import MacenkoNormalizer
from staintools import VahadaneNormalizer

from staintools import standardize_brightness
from staintools.utils.visual import read_image, show, show_colors, build_stack, patch_grid

import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
import matplotlib.image as matimg
from tqdm import tqdm

pic_path='stomach_pic/'
ref_path=pic_path+'reference_pic/reference_pic.jpg'

i1 = read_image(ref_path)

standard = standardize_brightness(i1)
plt.imshow(standard)
plt.show()
n = ReinhardNormalizer()
n.fit(i1)


r_img=pic_path+'raw_pic/raw_pic.jpg'
s_img=pic_path+'tar_pic/tar_pic.jpg'
i2=read_image(r_img)
target=n.transform(i2)
target=cv2.cvtColor(target,cv2.COLOR_RGB2BGR)
cv2.imwrite(s_img,target)
