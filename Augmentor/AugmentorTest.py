'''
数据增强，包括：随机水平翻转、随机垂直翻转、随机20度范围内的剪切、随机20%范围内的缩放、随机20%范围内的水平平移，随机20%范围内的垂直平移，
随机20度范围内的旋转。变换时，边界外像素点的填充采用“reflect”模式。图像均被缩放为256*256大小，像素值被调整到0-1之间。
'''

# this is import from Augmentor third-party package
# import Augmentor
#
# # create a new pipeline
# file_path = "C:\\liyu\\files\\tiff\\cells"
# p = Augmentor.Pipeline(file_path)


from Augmentor.Pipeline import *
import time

# create a new pipeline
file_path = "C:\\liyu\\files\\tiff\\newtest"
p = Pipeline(file_path)


# add operations to the pipeline

# 水平翻转
p.flip_left_right(probability=0.8)

# # 垂直翻转
# p.flip_top_bottom(probability=0.5)
#
# # 随机90， 180， 270 度旋转
# p.rotate_random_90(probability=0.75)
#
# # 随机20度内旋转，不变形, 四角填充黑色，图片大小不变
# p.rotate_without_crop(probability=0.5, max_left_rotation=20, max_right_rotation=20)
#
# # 随机20度内旋转，不变形, 四角填充黑色，图片大小调整
# p.rotate_without_crop(probability=0.5, max_left_rotation=20, max_right_rotation=20, expand=True)
#
# # 随机剪切, 中心不变
# p.crop_by_size(probability=0.5, width=100, height=100)
#
# # 随机剪切，中心变化，可调节剪切比例
# p.crop_random(probability=0.5, percentage_area=0.8)
#
# # 随机20%缩放，大小不变，图片缩小时以黑色填充
# p.zoom(probability=0.5, min_factor=0.8, max_factor=1.2)

# resize
p.resize(probability=1, width=256, height=256)


# execute and sample from the pipeline
time1 = time.time()

num_of_samples = 14200
p.sample(num_of_samples)

time2 = time.time()
print("time cost = " + str(time2-time1) + "s")