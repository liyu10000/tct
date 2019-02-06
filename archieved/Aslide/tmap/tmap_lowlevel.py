import copy
import ctypes
import math

import numpy as np
from ctypes import *
from itertools import count

from PIL import Image
from openslide import lowlevel

_lib = cdll.LoadLibrary('libiViewerSDK.so')


class _TmapSlide(object):
    def __init__(self, ptr):
        self._as_parameter = ptr
        self._valid = True

        self._close = close_tmap_file

    def __del__(self):
        if self._valid:
            self._close(self)

    def invalidate(self):
        self._valid = False

    @classmethod
    def from_param(cls, obj):
        if obj.__class__ != cls:
            raise ValueError("Not an TmapSlide reference")
        if not obj._as_parameter_:
            raise ValueError("Passing undefined slide object")
        if not obj._valid:
            raise ValueError("Passing closed TmapSlide object")
        return obj


# check for errors opening an image file and wrap the resulting handle
def _check_open(result, _func, _args):
    if result is None:
        raise lowlevel.OpenSlideUnsupportedFormatError(
            "Unsupported or missing image file")
    slide = _TmapSlide(c_void_p(result))

    return slide


# prevent further operations on slide handle after it is closed
def _check_close(_result, _func, args):
    args[0].invalidate()


# check if the library got into an error state after each library call
def _check_error(result, func, args):
    return lowlevel._check_string(result, func, args)


# Convert returned NULL-terminated char** into a list of strings
def _check_name_list(result, func, args):
    _check_error(result, func, args)
    names = []
    for i in count():
        name = result[i]
        if not name:
            break
        names.append(name.decode('UTF-8', 'replace'))
    return names


# resolve and return an OpenSlide function with the specified properties
def _func(name, restype, argtypes, errcheck=_check_error):
    func = getattr(_lib, name)
    func.argtypes = argtypes
    func.restype = restype
    # if errcheck is not None:
    #     func.errcheck = errcheck
    return func


def _handle_func(puc_list, W, H):
    length = W * H * 3
    try:
        data = ctypes.string_at(puc_list, length)
        data = np.fromstring(data, np.uint8).reshape((W, H, 3))
        data= data[:, :, ::-1]

        return Image.fromarray(np.asarray(data, dtype=np.uint8))
    except Exception as e:
        raise e


# 打开图像 函数
_open_tmap_file = _func('OpenTmapFile', c_void_p, None, _check_open)


def open_tmap_file(name):
    osr = _open_tmap_file(name, len(name))
    return osr


# 关闭图像 函数
close_tmap_file = _func('CloseTmapFile', None, [c_void_p], _check_close)

# 获取图层数 函数
get_focus_number = _func('GetFocusNumber', c_int, [c_void_p])

set_focus_layer = _func('SetFocusLayer', c_int, [c_void_p, c_int])

# 获取当前的对焦面数值
get_focus_layer = _func('GetFocusLayer', c_int, [c_void_p])

# 获取Tmap文件扫描时的分级数
get_layer_num = _func('GetLayerNum', c_int, [c_void_p])

# 获取Tmap文件的总共图像块数目
get_tile_mumber = _func('GetTileNumber', c_int, [c_void_p])

# 获取格式文件的版本号
get_tmap_version = _func('GetTmapVersion', c_int, [c_void_p])

# 获取Tmap文件扫描时的最大倍率
get_scan_scale = _func('GetScanScale', c_int, [c_void_p])


class ImgSize(Structure):
    _fields_ = [('imgsize', c_longlong),
                ('width', c_int),
                ('height', c_int),
                ('depth', c_int)
                ]


# 获取Tmap格式文件的整体图片信息
_get_image_info_ex = _func('GetImageInfoEx', ImgSize, [c_void_p, c_int])


def get_image_info_ex(slide, etype):
    img = _get_image_info_ex(slide, c_int(etype))
    return img


def get_dimensions(slide):
    img = get_image_info_ex(slide, 6)
    return (img.width, img.height)

def get_level_dimensions(slide):
    dimensions = get_dimensions(slide)
    z_size = dimensions
    level_dimensions = [z_size]

    while z_size[0] > 1 or z_size[1] > 1:
        z_size = tuple(max(1, int(math.ceil(z / 2))) for z in z_size)
        level_dimensions.append(z_size)

    return level_dimensions

def get_level_count(slide):
    return len(get_level_dimensions(slide))

def get_level_downsamples(slide):
    length = get_level_count(slide)
    return tuple(reversed([np.power(2, i) for i in range(length)]))

# 获取Tmap格式文件的整体图片信息
get_pixel_size = _func('GetPixelSize', c_int, [c_void_p])

# 获取Tmap格式文件的切片数字图像信息
_get_image_data = _func('GetImageData', c_int, [c_void_p, c_int, c_char_p, c_int])


def get_image_data(slide, etype):
    img_info = _get_image_info_ex(slide, c_int(etype))
    nBufferLength = int(img_info.width * img_info.height * img_info.depth / 8)
    pucImg = create_string_buffer(nBufferLength)
    img_data = _get_image_data(slide, c_int(etype), pucImg, nBufferLength)
    if img_data:
        return _handle_func(pucImg, img_info.height, img_info.width)

    return None


# 获取Tmap格式文件的数据
_get_image_size_ex = _func('GetImageSizeEx', ImgSize, [c_void_p, c_int, c_int, c_int, c_int, c_float])


def get_image_size_ex(slide, nLeft, nTop, nRight, nBottom, fScale):
    img_size = _get_image_size_ex(slide, nLeft, nTop, nRight, nBottom, fScale)
    return img_size


# 获取Tmap格式文件的切片数字图像
_get_crop_image_data_ex = _func('GetCropImageDataEx', POINTER(c_ubyte),
                                [c_void_p, c_int, c_int, c_int, c_int, c_int, c_float])


def get_crop_image_data_ex(slide, nIndex, nLeft, nTop, nRight, nBottom):
    fScale = get_scan_scale(slide)
    img_size = _get_image_size_ex(slide, nLeft, nTop, nRight, nBottom, fScale)
    nBufferLength = img_size.imgsize
    crop_image_data = _get_crop_image_data_ex(slide, c_int(nIndex), nLeft, nTop, nRight, nBottom, fScale, nBufferLength)

    return _handle_func(crop_image_data, img_size.height, img_size.width)


# 获取Tmap格式文件的切片数字图像
_get_tile_data = _func('GetTileData', POINTER(c_ubyte), [c_void_p, c_int, c_int, c_int])


# 获取传入序列位置对应的图像
def get_tile_data(slide, n_downsample_scale, n_tile_row, n_tile_col):
    tile_data = _get_tile_data(slide, n_downsample_scale, n_tile_row, n_tile_col)

    return _handle_func(tile_data, 256, 256)


def main():
    path = "/home/stimage/Development/DATA/TMAP/SZH1513139_N_4_20181220132441.TMAP"
    slide = open_tmap_file(path)

    print('get_focus_number:', get_focus_number(slide))

    print('get_tmap_version:', get_tmap_version(slide))

    print('get_layer_num', get_layer_num(slide))

    print('get_tile_mumber', get_tile_mumber(slide))

    print('########################################')
    print('get_scan_scale:', get_scan_scale(slide))

    print('########################################')
    print('get_focus_layer:', get_focus_layer(slide))

    print('set_focus_layer', set_focus_layer(slide, 0))

    img_info = get_image_info_ex(slide, 0)
    print('img_size:', img_info.imgsize)
    print("ImgInfo.width", img_info.width)
    print("ImgInfo.height", img_info.height)
    print("ImgInfo.depth", img_info.depth)

    print('###################################')
    img = get_image_data(slide, 0)
    img.show()

    print('###################################')
    print('get_pixel_size', get_pixel_size(slide))

    print('###################################')
    nLeft = 25600
    nTop = 25600
    nRight = 26600
    nBottom = 26600
    fScale = 40.0
    img_size = get_image_size_ex(slide, nLeft, nTop, nRight, nBottom, fScale)
    print(img_size)
    print("ImgSize.imgsize", img_size.imgsize)
    print("ImgSize.width", img_size.width)
    print("ImgSize.height", img_size.height)
    print("ImgSize.depth", img_size.depth)

    print('###################################')
    img = get_crop_image_data_ex(slide, 1, nLeft, nTop, nRight, nBottom, fScale)
    img.show()

    img = get_tile_data(slide, 1, 100, 121)
    img.show()
    close_tmap_file(slide)


if __name__ == '__main__':
    main()
