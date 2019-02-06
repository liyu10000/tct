# coding: UTF-8

import ctypes
from ctypes import *
# import cv2.cv as cv
import imageio
import numpy as np
import copy




ll = ctypes.cdll.LoadLibrary

lib = ll("./libiViewerSDK.so")
print('load successload success')


#h = lib.OpenTmapFile("./hx_er_00218.TMAP")

#pstr = '/1_data/Ki67/ki67_01101_01205/SLICEID$20181203175751.TMAP'
pstr = '/home/wqf/tiffs/szrm_tmap_20/SZH00561.TMAP'
p = c_wchar_p(pstr)
lib.OpenTmapFile.restype = c_void_p
h = c_void_p
h = lib.OpenTmapFile(pstr, len(pstr))




print("GetScanScale",lib.GetScanScale(h))


Version = lib.GetTmapVersion(h)
print("Version",Version)

LayerNum = lib.GetLayerNum(h)
print("LayerNum",LayerNum)


GetFocusNumber = lib.GetFocusNumber(h)
print("GetFocusNumber",GetFocusNumber)



GetTileNumber = lib.GetTileNumber(h)
print("GetTileNumber",GetTileNumber)



nFocus=c_int(0)
Foucus = lib.SetFocusLayer(h,nFocus)
print("Foucus",Foucus)


GetFocusLayer = lib.GetFocusLayer(h)
print("GetFocusLayer",GetFocusLayer)


GetPixelSize = lib.GetPixelSize(h)
print("GetPixelSize",GetPixelSize)


################################################################################

#etype=c_int(6)
etype=c_int(2)
class ImgSize(Structure):
    _fields_=[('imgsize',c_longlong),
              ('width',c_int),
              ('height',c_int),
              ('depth',c_int)
             ]


GetImageInfoEx_fun = lib.GetImageInfoEx
GetImageInfoEx_fun.restype = ImgSize

print("GetImageInfoEx_fun",GetImageInfoEx_fun(h,etype))

fun_ImgSize = GetImageInfoEx_fun(h,etype)
print("fun_ImgSize.imgsize",fun_ImgSize.imgsize)
print("fun_ImgSize.width",fun_ImgSize.width)
print("fun_ImgSize.height",fun_ImgSize.height)
print("fun_ImgSize.depth",fun_ImgSize.depth)


################################################################################


GetTileData_fun = lib.GetTileData
GetTileData_fun.restype = POINTER(c_ubyte)
b = GetTileData_fun(h, 1, 120, 100)
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

pic[:,:,0] = pic_channel_2
pic[:,:,1] = pic_channel_1
pic[:,:,2] = pic_channel_0

pic = np.asarray(pic, dtype=np.uint8)
# imageio.imwrite('/home/yuany/workspace/source/iViewerSDK-2017-Linux/testiViewerSDK/iViewerSDK/'+'test_120' + '.jpg', pic)


###########################################################################


nBufferLength = fun_ImgSize.width * fun_ImgSize.height * fun_ImgSize.depth / 8
nBufferLength = int(nBufferLength)
#nBufferLength = 256*256*24/8
#nBufferLength = fun_ImgSize.imgsize
print("nBufferLength",nBufferLength)
pucImg = create_string_buffer(nBufferLength)
#pucImg = POINTER(c_ubyte)
GetImageData = lib.GetImageData(h,etype,pucImg,nBufferLength)
print("GetImageData",GetImageData)


H=fun_ImgSize.width
W=fun_ImgSize.height

puc_list=[0 for i in range(W * H * 3)]
for i in range(W * H * 3):
    puc_list[i] = ord(pucImg[i])

pic = np.array(puc_list)
pic = pic.reshape((W,H,3))
pic_channel_0 = copy.copy(pic[:,:,0])
pic_channel_1 = copy.copy(pic[:,:,1])
pic_channel_2 = copy.copy(pic[:,:,2])
pic[:,:,0] = pic_channel_2
pic[:,:,1] = pic_channel_1
pic[:,:,2] = pic_channel_0

pic = np.asarray(pic, dtype=np.uint8)
# imageio.imwrite('/home/yuany/workspace/source/iViewerSDK-2017-Linux/testiViewerSDK/iViewerSDK/'+'test_GetImageData' + '.jpg', pic)



###############################################################################

GetImageSizeEx_fun = lib.GetImageSizeEx
GetImageSizeEx_fun.restype = ImgSize

nLeft = c_int(25600)
nTop = c_int(25600)
nRight = c_int(26600)
nBottom = c_int(26600)
fScale = c_float(40.0)
'''
nLeft = c_int(516)
nTop = c_int(0)
nRight = c_int(15290)
nBottom = c_int(16320)
fScale = c_float(1.25)
'''
print("GetImageSizeEx_fun",GetImageSizeEx_fun(h,nLeft,nTop,nRight,nBottom,fScale))

fun_ImgSize = GetImageSizeEx_fun(h,nLeft,nTop,nRight,nBottom,fScale)
print("fun_ImgSize.imgsize",fun_ImgSize.imgsize)
print("fun_ImgSize.width",fun_ImgSize.width)
print("fun_ImgSize.height",fun_ImgSize.height)
print("fun_ImgSize.depth",fun_ImgSize.depth)


#################################################################################

nIndex = c_int(1)
nBufferLength = fun_ImgSize.imgsize

GetCropImageDataEx_fun = lib.GetCropImageDataEx
GetCropImageDataEx_fun.restype = POINTER(c_ubyte)
f = GetCropImageDataEx_fun(h, nIndex, nLeft, nTop, nRight, nBottom, fScale, nBufferLength)

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

pic[:,:,0] = pic_channel_2
pic[:,:,1] = pic_channel_1
pic[:,:,2] = pic_channel_0

pic = np.asarray(pic, dtype=np.uint8)
# imageio.imwrite('/home/yuany/workspace/source/iViewerSDK-2017-Linux/testiViewerSDK/iViewerSDK/'+'test_GetCropImageDataEx' + '.jpg', pic)

#################################################################################



nIndex = c_int(1)
nBufferLength = fun_ImgSize.imgsize

pucbuffer = create_string_buffer(nBufferLength)
GetCropImageData_fun = lib.GetCropImageData
fbool = GetCropImageData_fun(h, nIndex, nLeft, nTop, nRight, nBottom, fScale, pucbuffer, nBufferLength)
print("fbool",fbool)
print("pucbuffer",sizeof(pucbuffer))
print("pucbuffer",pucbuffer[0],type(pucbuffer[0]),ord(pucbuffer[0]))


W=fun_ImgSize.width
H=fun_ImgSize.height

puc_list=[0 for i in range(W * H * 3)]
for i in range(W * H * 3):
    #print i,"b[]:",repr(b[i])
    puc_list[i] = ord(pucbuffer[i])

pic = np.array(puc_list)
pic = pic.reshape((W,H,3))
pic_channel_0 = copy.copy(pic[:,:,0])
pic_channel_1 = copy.copy(pic[:,:,1])
pic_channel_2 = copy.copy(pic[:,:,2])
pic[:,:,0] = pic_channel_2
pic[:,:,1] = pic_channel_1
pic[:,:,2] = pic_channel_0

pic = np.asarray(pic, dtype=np.uint8)
# imageio.imwrite('/home/yuany/workspace/source/iViewerSDK-2017-Linux/testiViewerSDK/iViewerSDK/'+'test_GetCropImageData' + '.jpg', pic)

#################################################################################






lib.CloseTmapFile(h)

print("*********finish******")