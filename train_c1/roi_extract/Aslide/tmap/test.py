# coding: UTF-8

import ctypes
from ctypes import *
import imageio
import numpy as np
import copy
ll = ctypes.cdll.LoadLibrary

lib = ll("./lib/libiViewerSDK.so")

print('load successload success')

path = "/media/wqf/4adb4c9e-80d5-43fd-8bf8-c4d8f353091f/tsimage/tiffs_un/SZH1513139_N_4_20181220132441.TMAP"

lib.OpenTmapFile.restype = c_void_p
# *****************************************************************************************************
#	    功能： 打开Tmap格式的文件，该函数被最先调用，才能进行后续操作，支持多线程打开多个Tmap文件或同一个Tmap文件，通过hFile区
#	        分不同的线程,如果对用一个打开的文件再次调用该函数，表示建立一个新连接，获得一个新句柄，请在相关的线程中使用这个句柄。
#       参数： pFile 要打开的Tmap格式文件，例如"c:\\abc.tmap"
#             hFile 如果打开成功，则获得该文件的句柄，以后通过该句柄对该文件进行操作
# 	    返回： 打开成功，返回True，并获得hFile；打开失败，返回False。
# *****************************************************************************************************
slide = lib.OpenTmapFile(path, len(path))
print(slide)

lib.GetScanScale.argtypes = [c_void_p]
#*****************************************************************************************************
#       功能： 取得Tmap文件扫描时的分级数。分级原则是原始图像宽度不断除以2，直到图像宽度小于256为止，除的次数就是分级数。
#       参数： hFile 要访问的Tmap格式文件的句柄。
#       返回： 读取成功，返回分级数；读取失败，返回0。
#*****************************************************************************************************
print("GetScanScale",lib.GetScanScale(slide))

lib.GetTmapVersion.argtypes = [c_void_p]
# *****************************************************************************************************
#       功能： 取得Tmap格式文件的版本号。
#       参数： hFile 要访问的Tmap格式文件的句柄。
#       返回： 读取成功，返回文件版本号；读取失败，返回0。
# *****************************************************************************************************
Version = lib.GetTmapVersion(slide)
print("Version",Version)

lib.GetLayerNum.argtypes = [c_void_p]
LayerNum = lib.GetLayerNum(slide)
print("LayerNum",LayerNum)

lib.GetFocusNumber.argtypes = [c_void_p]
#*****************************************************************************************************
#       功能： 取得Tmap文件的对焦层数。对于单层扫描图像，返回1。对于多层扫描，返回扫描层数。
#       参数： hFile 要访问的Tmap格式文件的句柄。
#       返回： 读取成功，返回图像扫描层数；读取失败，返回0。
#*****************************************************************************************************
GetFocusNumber = lib.GetFocusNumber(slide)
print("GetFocusNumber",GetFocusNumber)

lib.GetTileNumber.argtypes = [c_void_p]
#*****************************************************************************************************
#       功能： 取得Tmap文件的总共图像块数目。每个图像都是由若干图像块组成，每个图像块大小为256*256。
#       参数： hFile 要访问的Tmap格式文件的句柄。
#       返回： 读取成功，返回图像块数；读取失败，返回0。
#*****************************************************************************************************
GetTileNumber = lib.GetTileNumber(slide)
print("GetTileNumber",GetTileNumber)



nFocus=0
lib.SetFocusLayer.argtypes = [c_void_p, c_int]
#*****************************************************************************************************
#       功能： 设置当前的对焦面。对单层扫描来说，只有一个对焦面。对多层扫描来说，高于最佳对焦面为正，低于最佳对焦面为负
#       参数： hFile 要访问的Tmap格式文件的句柄。
#       返回： 设置成功，true；读取失败，返回false。
#*****************************************************************************************************
Foucus = lib.SetFocusLayer(slide, nFocus)
print("Foucus",Foucus)

lib.GetFocusLayer.argtypes = [c_void_p]
#*****************************************************************************************************
#       功能： 读取当前的对焦面数值。
#       参数： hFile 要访问的Tmap格式文件的句柄。
#       返回： 读取成功，返回当前的对焦面数值。
#*****************************************************************************************************
GetFocusLayer = lib.GetFocusLayer(slide)
print("GetFocusLayer",GetFocusLayer)

lib.GetPixelSize.argtypes = [c_void_p]

GetPixelSize = lib.GetPixelSize(slide)
print("GetPixelSize",GetPixelSize)


################################################################################

etype=6
class ImgSize(Structure):
    _fields_=[('imgsize',c_longlong),
              ('width',c_int),
              ('height',c_int),
              ('depth',c_int)
             ]


lib.GetImageInfoEx.restype = ImgSize
lib.GetImageInfoEx.argtypes = [c_void_p, c_int]
#*****************************************************************************************************
#       功能： 取得Tmap格式文件的整体图片信息
#       参数： hFile 要访问的Tmap格式文件的句柄
#        _      TMAP_IMAGE_TYPE eType, 获取图像的类型，参见前面说明
#               nWidth 获取图片的宽度
#               nHeight 获取图片的高度
#               nColor 获取图像的像素位数， 彩色是24bits，黑白是8bits
#       返回： 返回图像占用的字节数
#*****************************************************************************************************
fun_ImgSize = lib.GetImageInfoEx(slide, etype)
print("fun_ImgSize.imgsize",fun_ImgSize.imgsize)
print("fun_ImgSize.width",fun_ImgSize.width)
print("fun_ImgSize.height",fun_ImgSize.height)
print("fun_ImgSize.depth",fun_ImgSize.depth)


################################################################################

lib.GetTileData.restype = POINTER(c_ubyte)
lib.GetTileData.argtypes = [c_void_p, c_int, c_int, c_int]
b = lib.GetTileData(slide, 1, 120, 100)
print(sizeof(b))
print(type(b))

pic_list=[0 for i in range(256*256*3)]
for i in range(256*256*3):
    #print i,"b[]:",repr(b[i])
    pic_list[i] = repr(b[i])

pic = np.array(pic_list)
pic = pic.reshape((256,256,3))
pic_channel_0 = copy.copy(pic[:,:,0])
pic_channel_1 = copy.copy(pic[:,:,1])
pic_channel_2 = copy.copy(pic[:,:,2])

pic[:,:,0] = pic_channel_1
pic[:,:,1] = pic_channel_2
pic[:,:,2] = pic_channel_0

pic = np.asarray(pic, dtype=np.uint8)
imageio.imwrite('/tmp/'+'test_120' + '.jpg', pic)




###############################################################################

GetImageSizeEx_fun = lib.GetImageSizeEx
GetImageSizeEx_fun.restype = ImgSize

nLeft = 25600
nTop = 25600
nRight = 26600
nBottom = 26600
fScale = 40.0

GetImageSizeEx_fun.argtypes = [c_void_p, c_int, c_int, c_int, c_int, c_float]
fun_ImgSize = GetImageSizeEx_fun(slide, nLeft, nTop, nRight, nBottom, fScale)

print("fun_ImgSize.imgsize",fun_ImgSize.imgsize)
print("fun_ImgSize.width",fun_ImgSize.width)
print("fun_ImgSize.height",fun_ImgSize.height)
print("fun_ImgSize.depth",fun_ImgSize.depth)


#################################################################################

nIndex = c_int(1)
nBufferLength = fun_ImgSize.imgsize
GetCropImageDataEx_fun = lib.GetCropImageDataEx
GetCropImageDataEx_fun.restype = POINTER(c_ubyte)
GetCropImageDataEx_fun.argtypes = [c_void_p, c_int, c_int, c_int, c_int, c_int, c_float]
f = GetCropImageDataEx_fun(slide, nIndex, nLeft, nTop, nRight, nBottom, fScale, nBufferLength)

print("f",sizeof(f))
print("f",f[0])
print("f",f)


W=fun_ImgSize.width
H=fun_ImgSize.height

puc_list=[0 for i in range(W * H * 3)]
for i in range(W * H * 3):
    #print i,"b[]:",repr(b[i])
    puc_list[i] = f[i]

pic = np.array(puc_list)
pic = pic.reshape((W,H,3))
pic_channel_0 = copy.copy(pic[:,:,0])
pic_channel_1 = copy.copy(pic[:,:,1])
pic_channel_2 = copy.copy(pic[:,:,2])

pic[:,:,0] = pic_channel_1
pic[:,:,1] = pic_channel_2
pic[:,:,2] = pic_channel_0

pic = np.asarray(pic, dtype=np.uint8)
imageio.imwrite('/tmp/'+'test_GetCropImageData' + '.jpg', pic)

#################################################################################

lib.CloseTmapFile.argtypes = [c_void_p]
#*****************************************************************************************************
#   功能： 关闭Tmap格式的文件，该函数被最后调用
#   参数： hFile 要关闭的Tmap格式文件的句柄
#   返回： 关闭成功，返回True；关闭失败，返回False。
#*****************************************************************************************************
lib.CloseTmapFile(slide)

print('*********finish******')




