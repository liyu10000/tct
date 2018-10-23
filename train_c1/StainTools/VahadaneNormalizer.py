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

pic_path='lbp_pic/'
ref_path=pic_path+'reference_pic/zs_abnormal.png'

n = VahadaneNormalizer()
n.fit(i1)
input_dir = 'lbp_pic/raw_pic/dif_hospi/'
output_dir = 'lbp_pic/tar_pic/dif_hospi_1/'
pics = os.listdir(input_dir)
for pic in pics:
    r_img=read_image(input_dir+pic)
    target=n.transform(r_img)
    target=cv2.cvtColor(target,cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_dir+pic,target) 
