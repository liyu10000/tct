from easydict import EasyDict as edict
from multiprocessing import cpu_count
import os

curr_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

__C = edict()
# Consumers can get config by:
#   from config import cfg
cfg = __C

#
# lbp algo param
#
__C.lbp = edict()
__C.lbp.angle = 0


#
# darknet param
#
__C.darknet = edict()
__C.darknet.classes = ["ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]
__C.darknet.dartnetlib = os.path.join(curr_path, "models/darknet/libdarknet.so")
__C.darknet.cfg_file = os.path.join(curr_path, "models/darknet/yolov3-minitest-infer.cfg")
__C.darknet.weights_file = os.path.join(curr_path, "dataset_files/yolov3-sota.weights")
__C.darknet.datacfg_file = os.path.join(curr_path, "models/darknet/minitest.data")
__C.darknet.namecfg_file = os.path.join(curr_path, "models/darknet/minitest.names")

#
# xception param
#
__C.xception = edict()
__C.xception.det1 = 0.05  # used in gen_np_array
__C.xception.size = 299
__C.xception.weights_file = os.path.join(curr_path, "dataset_files/Xception_finetune.h5")
__C.xception.classes = ["ACTINO", "ADC", "AGC1", "AGC2", "ASCH", "ASCUS", "CC", "EC", "FUNGI", 
                        "GEC", "HSIL", "LSIL", "MC", "RC", "SC", "SCC", "TRI", "VIRUS"]
__C.xception.det2 = 0.1   # used in gen output csv file


#
# xgboost param
#
__C.xgboost = edict()
__C.xgboost.pkl_file = os.path.join(curr_path, "dataset_files/XGBClassifier.pkl")
__C.xgboost.classes = ["NORMAL", "ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]

#
# process param
#
__C.process = edict()
__C.process.angle = 0

#
# data param
#
__C.data = edict()
__C.data.angle = 0


#
# slice param
#
__C.slice = edict()
# 切图-宽
__C.slice.WIDTH = 608
# 切图-高
__C.slice.HEIGHT = 608
# 切图步长
__C.slice.DELTA = 608
# 切图比例-开始
__C.slice.AVAILABLE_PATCH_START_RATIO = 0.1
# 切图比例-结束
__C.slice.AVAILABLE_PATCH_END_RATIO = 0.9
# 过滤低价值图像阈值
__C.slice.THRESH = 10.0
# 切图进程数量
__C.slice.SLICE_PROCESS_NUM = cpu_count() - 6

# 仅截取大图中间指定大小区域
__C.center = edict()
# 切图数量
__C.center.PATCH_NUM = 128
# 切图尺寸-宽
__C.center.PATCH_WIDTH = 224
# 切图尺寸-高
__C.center.PATCH_HEIGHT = 224
# 切图步长
__C.center.DELTA = 224

# 生产环境细胞分割默认参数
__C.algo = edict()
__C.algo.patch_lens = 30
__C.algo.thresh = .1
__C.algo.hier_thresh = .1
__C.algo.nms = .1
__C.algo.DEFAULT_WIDTH = 299
__C.algo.DEFAULT_HEIGHT = 299

# 返回值编码
__C.code = edict()
# success
__C.code.success = 0
# fail
__C.code.fail = -1

