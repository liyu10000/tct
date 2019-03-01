# note: only works for python-32bit
import sys
from ctypes import *

class ImageInfoStruct(Structure):
    _fields_ = [ ("DataFilePTR", c_void_p) ]

if sys.platform == "linux" or sys.platform == "linux2":
    lib = cdll.LoadLibrary("libImageOperationLib.so")
elif sys.platform == "win32":
    lib = WinDLL("ImageOperationLib.dll")
else:
    print("operating system not supported")
    sys.exit()
image = ImageInfoStruct()

lib.InitImageFileFunc.argtypes = [POINTER(ImageInfoStruct), c_char_p]
lib.InitImageFileFunc.restype = c_int
path = c_char_p(b"./test.kfb")
lib.InitImageFileFunc(byref(image), path)
print("opened image")

lib.GetHeaderInfoFunc.argtypes = [ImageInfoStruct, POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_float), POINTER(c_double), POINTER(c_float), POINTER(c_int)]
lib.GetHeaderInfoFunc.restype = c_int
scan_height = scan_width = scan_scale = block_size = c_int()
spend_time = cap_res = c_float()
scan_time = c_double()
lib.GetHeaderInfoFunc(image, byref(scan_height), byref(scan_width), byref(scan_scale), byref(spend_time), byref(scan_time), byref(cap_res), byref(block_size))
print("got header info: ", scan_width.value, scan_height.value, scan_scale.value, spend_time.value)

# lib.GetImageStreamFunc.argtypes = [POINTER(ImageInfoStruct), c_float, c_int, c_int, POINTER(c_int), POINTER(c_char_p)]
# lib.GetImageStreamFunc.restype = c_char_p
# scale = c_float(20.0)
# pos_x = pos_y = c_int(0)
# length = c_int()
# stream = c_char_p()
# lib.GetImageStreamFunc(byref(image), scale, pos_x, pos_y, byref(length), byref(stream))
# print("got image stream: ", scale.value, pos_x.value, pos_y.value, length.value)

# # not defined?
# lib.GetImageRGBDataStreamFunc.argtypes = [POINTER(ImageInfoStruct), c_float, c_int, c_int, POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_char_p)]
# lib.GetImageRGBDataStreamFunc.restype = c_char_p
# scale = c_float(20.0)
# pos_x = pos_y = c_int(0)
# length = c_int()
# width = height = c_int()
# stream = c_char_p()
# lib.GetImageRGBDataStreamFunc(byref(image), scale, pos_x, pos_y, byref(length), byref(width), byref(height), byref(stream))
# print("got image stream: ", width.value, height.value)

lib.GetImageDataRoiFunc.argtypes = [ImageInfoStruct, c_float, c_int, c_int, c_int, c_int, POINTER(c_char_p), POINTER(c_int), c_bool]
lib.GetImageDataRoiFunc.restype = c_int
scale = c_float(20.0)
x = c_int(4096)
y = c_int(0)
size = c_int(4096)
buffer = c_char_p()
length = c_int()
lib.GetImageDataRoiFunc(image, scale, x, y, size, size, byref(buffer), byref(length), True)
print("got roi at: ", x.value, y.value)

# name = str(x.value) + "_" + str(y.value) + ".jpg"
# f = open(name, "wb")
# f.write(string_at(buffer, length.value))
# f.close()

lib.UnInitImageFileFunc.argtypes = [POINTER(ImageInfoStruct)]
lib.UnInitImageFileFunc.restype = c_int
lib.UnInitImageFileFunc(byref(image))
print("done.")