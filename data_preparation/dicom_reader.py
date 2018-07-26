import os
import pydicom
import matplotlib.pyplot as plt
from utils.scan_files import scan_files

dcms = scan_files("C:\\Users\\tsimage\\Desktop\\lung\\李京", postfix=".dcm")
save_path = "../res/temp/test"
if not os.path.exists(save_path):
    os.mkdir(save_path)
for dcm in dcms:
    name = os.path.splitext(os.path.basename(dcm))[0]
    ds = pydicom.dcmread(dcm)
    plt.imsave(os.path.join(save_path, name+".jpg"), ds.pixel_array)
    print(name + " saved")
