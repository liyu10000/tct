import os
import cv2
import openslide
import numpy as np
from skimage.filters import threshold_otsu
# from tslide import tslide


class WSIROI:
    def __init__(self, wsi_name):
        """ get a circle roi of wsi file, it should encampus almost all the cells area 
        :param wsi_name: wsi full file name
        :return dimensions: slide width,height in level 0
        :return center: center x,y of roi circle
        :return radius: radius of roi circle
        """
        slide = openslide.OpenSlide(wsi_name)
        dimensions = slide.dimensions
        levels = slide.level_count
        level = levels - 1
        downsample = slide.level_downsamples[level]
        print(level, downsample)
        thumbnail_rgb = cv2.cvtColor(np.asarray(slide.read_region((0, 0), level, slide.level_dimensions[level]).convert('RGB')), cv2.COLOR_RGB2GRAY)
        
        tissue_mask = thumbnail_rgb > threshold_otsu(thumbnail_rgb)
        kernel_size = (5, 5)
        kernel = np.ones(kernel_size, np.uint8)
        img = np.asarray(tissue_mask * 255, dtype=np.uint8)
        
        dilation = cv2.dilate(img, kernel, iterations=1)
        erosion = cv2.erode(dilation, kernel, iterations=5)
        
        dilation = cv2.dilate(erosion, kernel, iterations=1)
        img2, contours, hierarchy = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        cnt = contours[0]
        (x,y),radius = cv2.minEnclosingCircle(cnt)
        
        # convert top level dimension to bottom level dimension
        # center = (int(x),int(y))  # h,w is reverted when image object is converted to numpy array
        center = (int(y*downsample), int(x*downsample))
        radius = int(radius//3*2*downsample)
        
        slide.close()

        self.center = center
        self.radius = radius


    def in_roi(self, x_y, w_h):
        """ calculate if window is in roi circle 
        :param x_y: (x,y) of top-left window
        :param w_h: (w,h) of window
        """
        x, y = x_y
        w, h = w_h
        vertices = [(x,y), (x+w,y), (x+w,y+h), (x,y+h)]
        for vertex in vertices:
            distance_square = (vertex[0] - self.center[0])**2 + (vertex[1] - self.center[1])**2
            if distance_square > self.radius**2:
                return False
        return True


def get_roi(wsi_name):
    """ get a circle roi of wsi file, it should encampus almost all the cells area 
    :param wsi_name: wsi full file name
    :return dimensions: slide width,height in level 0
    :return center: center x,y of roi circle
    :return radius: radius of roi circle
    """
    slide = openslide.OpenSlide(wsi_name)
    dimensions = slide.dimensions
    levels = slide.level_count
    level = levels - 1
    downsample = slide.level_downsamples[level]
    print(level, downsample)
    thumbnail_rgb = cv2.cvtColor(np.asarray(slide.read_region((0, 0), level, slide.level_dimensions[level]).convert('RGB')), cv2.COLOR_RGB2GRAY)
    
    tissue_mask = thumbnail_rgb > threshold_otsu(thumbnail_rgb)
    kernel_size = (5, 5)
    kernel = np.ones(kernel_size, np.uint8)
    img = np.asarray(tissue_mask * 255, dtype=np.uint8)
    
    dilation = cv2.dilate(img, kernel, iterations=1)
    erosion = cv2.erode(dilation, kernel, iterations=5)
    
    dilation = cv2.dilate(erosion, kernel, iterations=1)
    img2, contours, hierarchy = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    cnt = contours[0]
    (x,y),radius = cv2.minEnclosingCircle(cnt)
    
    # convert top level dimension to bottom level dimension
    # center = (int(x),int(y))  # h,w is reverted when image object is converted to numpy array
    center = (int(y*downsample), int(x*downsample))
    radius = int(radius//3*2*downsample)
    
    slide.close()
    
    return dimensions, center, radius


def in_roi(x_y, w_h, center, radius):
    """ calculate if window is in roi circle 
    :param x_y: (x,y) of top-left window
    :param w_h: (w,h) of window
    :param center: (x,y) of roi circle
    :param radius: radius of roi circle
    """
    x, y = x_y
    w, h = w_h
    vertices = [(x,y), (x+w,y), (x+w,y+h), (x,y+h)]
    for vertex in vertices:
        distance_square = (vertex[0] - center[0])**2 + (vertex[1] - center[1])**2
        if distance_square > radius**2:
            return False
    return True


def count_by_roi(wsi_name, size=1216):
    """ count number of windows in roi circle """
    dimensions, center, radius = get_roi(wsi_name)
    print(dimensions, center, radius)
    count = 0
    for x in range(0, dimensions[0], size):
        for y in range(0, dimensions[1], size):
            count += 1 if in_roi((x,y), (size,size), center, radius) else 0
    return count


def get_dimensions(wsi_name):
    """ get slide dimension, at bottom level """
    slide = openslide.OpenSlide(wsi_name)
    dimensions = slide.dimensions
    slide.close()
    return dimensions


def count_by_range(wsi_name, factor=0.1, size=1216):
    """ count number of windows in center region from 0.1 to 0.9 """
    dimensions = get_dimensions(wsi_name)
    pad_w, pad_h = int(dimensions[0]*factor), int(dimensions[1]*factor)
    count = 0
    for x in range(pad_w, dimensions[0]-pad_w, size):
        for y in range(pad_h, dimensions[1]-pad_h, size):
            count += 1
    return count


if __name__ == "__main__":
    wsi_name = "2017-10-11 17_45_42.tif"
    size = 1216
    print("count by roi", count_by_roi(wsi_name, size))
    
    factor = 0.1
    size = 1216
    print("count by range", count_by_range(wsi_name, factor, size))