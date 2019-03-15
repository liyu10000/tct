#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 13:52:06 2019

@author: tsimage07
"""

images_dict = {}
Images_dict = []


import cv2
import os
import numpy as np

root = "/home/sakulaki/Development/rls/data/cells_test_0308/"

file_list = os.listdir(root)

for file in file_list:
    print(file)
    files = os.listdir(root + file)
    images_dict = {}
    for child in files:
        if child == "SC":
            sc_dict = []
            for f in os.listdir(root + file + '/' + child):
                print(f)
                if f.endswith('bmp'):
                    img = cv2.imread(root + file + '/' + child + '/' + f)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    np.savez(root + file + '/' + child + '/' + f.split('.bmp')[0] + '.npz', img)
                    sc_dict.append({"xception_data_path": root + file + '/' + child + '/' + f.split('.bmp')[0] + '.npz', "dna_area_ratio":0, \
                                    "dna_gray_ratio":0})
            images_dict["SC"] = sc_dict
        if child == "ASCUS":
            sc_dict = []
            for f in os.listdir(root + file + '/' + child):
                print(f)
                if f.endswith('bmp'):
                    img = cv2.imread(root + file + '/' + child + '/' + f)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    np.savez(root + file + '/' + child + '/' + f.split('.bmp')[0] + '.npz', img)
                    sc_dict.append({"xception_data_path": root + file + '/' + child + '/' + f.split('.bmp')[0] + '.npz', "dna_area_ratio":0, \
                                    "dna_gray_ratio":0})
            images_dict["ASCUS"] = sc_dict
        if child == "HSIL_S":
            sc_dict = []
            for f in os.listdir(root + file + '/' + child):
                print(f)
                if f.endswith('bmp'):
                    img = cv2.imread(root + file + '/' + child + '/' + f)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    np.savez(root + file + '/' + child + '/' + f.split('.bmp')[0] + '.npz', img)
                    sc_dict.append({"xception_data_path": root + file + '/' + child + '/' + f.split('.bmp')[0] + '.npz', "dna_area_ratio":0, \
                                    "dna_gray_ratio":0})
            images_dict["HSIL_S"] = sc_dict
    Images_dict.append(images_dict)