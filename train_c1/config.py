# Configuration file for LBP algorithm.
# Naming convention is that all variables are wrote in capital letter
#   with underscore as separator.

import os
from os.path import join as pjoin

TYPE_14_CLASS_DICT = {  
    # 微生物感染
    "FUNGI": "20_FUNGI",   # 1203  285 王悦
    "TRI": "21_TRI",       # 5002  198
    "CC": "22_CC",         # 6663  1203
    "ACTINO": "23_ACTINO", # 4958  972
    "VIRUS": "24_VIRUS",   # 881   110
    # 鳞状上皮异常
    "ASCUS": "25_ASCUS",   # 8574  1543 李冰
    "LSIL": "26_LSIL",     # 21927 3051    
    "ASC-H": "27_ASCH",    # 1102  367
    "HSIL": "28_HSIL",     # 17390 2027    
    "SCC": "29_SCC",       # 1962  260
    # 腺上皮异常
    "AGC1": "210_AGC1",    # 862   108 增强后: 10042   1081
    "AGC2-3": "211_AGC2",  # 508               6857    0
    "ADC": "212_ADC",      # 812               5829    0
    # 子宫内膜细胞（>40 岁妇女）
    "EC": "213_EC"         # 419   56          6385    826
}

TYPE_3_CLASS_DICT = {  
    # 微生物感染
    "FUNGI": "10_Infection",
    "TRI": "10_Infection",   
    "CC": "10_Infection",
    "ACTINO": "10_Infection",
    "VIRUS": "10_Infection",
    # 鳞状上皮异常
    "ASCUS": "11_Squamous",   
    "ASC-H": "11_Squamous",  
    "LSIL": "11_Squamous",
    "HSIL": "11_Squamous", 
    "SCC": "11_Squamous",
    # 腺上皮异常
    "AGC1": "12_Glandular",
    "AGC2-3": "12_Glandular",
    "ADC": "12_Glandular",
    # 子宫内膜细胞（>40 岁妇女）
    "EC": "12_Glandular"
}


# n-class classification
NUM_CLASSES = 4
# train inception
class_type = "12_Glandular"

LOG_DIR = "log"
PATCH_ARR_DIR = "arrange_patches_"+class_type
MODEL_CP_DIR = "model_checkpoints/train_patches_"+class_type


# SYSTEM
NUM_CORE_USE = 32
RANDOM_SEED = 666
RAND_NUM = 6
SPLIT_RATIO = [0.8, 0.1, 0.1]


# COLOR_REF_PATH
COLOR_REF_PATH = "staintools/abnormal_dim_10240.jpg"


# possible WSI extensions
WSI_EXT = ["tif", "svs", "ndpi", "tiff"]

# PATCH EXTRACTION
MIN_PATCH_SIZE = 299
MAX_PATCH_SIZE = 4096
PATCH_MASK_RATIOS = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0]
PATCH_SIZES = [299, 608, 768, 1024, 1536, 2048]

# ratio/fix
CUT_MODE = "fix"

ROI_LEVEL = -1
ROI_TYPE = "simple"
ROI_REGION_RATIO = 0.05
ROI_RATIO = 0.5
ROI_SIZE = [299, 608, 768, 1024, 1536, 2048]

HEAT_THRES = 0.5

# CONVNET
PATCH_BATCH_SIZE = 64
TRAIN_EPOCH = 50
TOP_EPOCH = 20
FINE_TUNE_EPOCH = 20

# size of the FC layer on top
TOP_FC_SIZE = 2048

# dimension of input data
# InceptionV3
IMG_WIDTH, IMG_HEIGHT = 299, 299
TRAIN_FROM_SCRATCH_LR = 1e-3

TOP_LAYER_LR = 1e-3

FINE_TUNE_LR = 1e-3

SAVE_BEST_ONLY = False
