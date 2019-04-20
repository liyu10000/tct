import cv2
import numpy as np
from skimage.filters import threshold_otsu
from Aslide import aslide


class WSIROI:

    def __init__(self, wsi_name):
        self.wsi_name = wsi_name
        self.find_roi()


    def find_roi(self):
        slide = aslide.Aslide(self.wsi_name)
        m, n = slide.dimensions
        level = slide.level_count - 1
        #self.downsample = slide.level_downsamples[level]
        thumbnail = slide.read_region((0, 0), level, slide.level_dimensions[level]).convert('RGB')
        slide.close()

        t_m, t_n = thumbnail.size
        self.downsample = (m/t_m + n/t_n) / 2
        self.thumbnail = np.array(thumbnail)
        
        img_gray = cv2.cvtColor(self.thumbnail, cv2.COLOR_RGB2GRAY)
        img_gray = cv2.pyrDown(img_gray)
        img_gray = cv2.pyrDown(img_gray)
        
        kernel_size = (5, 5)
        kernel = np.ones(kernel_size, np.uint8)
        img_open = cv2.morphologyEx(img_gray, cv2.MORPH_OPEN, kernel, iterations=3)
        # img_open = cv2.morphologyEx(img_open, cv2.MORPH_CLOSE, kernel, iterations=1)

        img_mask = img_open > threshold_otsu(img_open) / 0.99
        img_pool = self.maxpooling(img_mask, kernel_size=(1, 5))
        img_pool = self.maxpooling(img_pool, kernel_size=(5, 1))

        img, contours, hierarchy = cv2.findContours(img_pool.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        self.hull = cv2.convexHull(contours[1], False) * 4
        area = cv2.contourArea(self.hull)*self.downsample*self.downsample
        self.area_ratio = area/m/n
        self.m = m
        self.n = n
        

    def get_area_ratio(self):
        return self.area_ratio  # float between 0.0 and 1.0


    def get_roi(self):
        return self.hull  # np.ndarray, (num, 1, 2)


    def get_thumbnail(self):
        return self.thumbnail


    def get_downsample(self):
        return self.downsample
    
    
    def get_dimensions(self):
        return (self.m, self.n)


    def in_roi_simplified(self, x, y, w, h):
        center_x = (x + w / 2) / self.downsample
        center_y = (y + h / 2) / self.downsample
        return cv2.pointPolygonTest(self.hull, (center_x, center_y), False) == 1


    def in_roi_completed(self, x, y, w, h):
        x /= self.downsample
        y /= self.downsample
        w /= self.downsample
        h /= self.downsample
        points = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
        for point in points:
            if 1 != cv2.pointPolygonTest(self.hull, point, False):
                return False
        return True


    def maxpooling(self, img, kernel_size):
        h, w = img.shape
        img_pool = np.ones((h, w))
        h_win_size, w_win_size = kernel_size
        margin = 10
        for j in range(margin, h//2-margin):
            for i in range(margin, w//2-margin):
                img_pool[j][i] = np.max(img[j:j+h_win_size, i:i+w_win_size])
        for j in range(h//2-margin, h-margin):
            for i in range(margin, w//2-margin):
                img_pool[j][i] = np.max(img[j-h_win_size:j, i:i+w_win_size])
        for j in range(margin, h//2-margin):
            for i in range(w//2-margin, w-margin):
                img_pool[j][i] = np.max(img[j:j+h_win_size, i-w_win_size:i])
        for j in range(h//2-margin, h-margin):
            for i in range(w//2-margin, w-margin):
                img_pool[j][i] = np.max(img[j-h_win_size:j, i-w_win_size:i])
        return img_pool.astype(np.uint8)


def plot(image, x, y, w, h, downsample):
    x = int(x / downsample)
    y = int(y / downsample)
    w = int(w / downsample)
    h = int(h / downsample)
    cv2.rectangle(image, (x, y), (x+w, y+h), (255,0,0), 2)



if __name__ == "__main__":
    wsi_name = "TC19016138.TMAP"
    thumb_name = "./TC19016138.jpg"

    wsi_roi = WSIROI(wsi_name)

    area_ratio = wsi_roi.get_area_ratio()
    hull = wsi_roi.get_roi()
    print(area_ratio, hull.shape)
    
    downsample = wsi_roi.get_downsample()
    m, n = wsi_roi.get_dimensions()
    i_start, i_end = int(m * 0.05), int(m * 0.95)
    j_start, j_end = int(n * 0.05), int(n * 0.95)
    size = 1216

    count = 0
    thumbnail = wsi_roi.get_thumbnail()
    thumbnail = cv2.cvtColor(thumbnail, cv2.COLOR_RGB2BGR)
    for i in range(i_start, i_end, size):
        for j in range(j_start, j_end, size):
            is_in1 = wsi_roi.in_roi_simplified(i, j, size, size)
            is_in2 = wsi_roi.in_roi_completed(i, j, size, size)
            # print(i, j, is_in1, is_in2)
            if is_in2:
                count += 1
                plot(thumbnail, i, j, size, size, downsample)
    print(count)
    
    cv2.imwrite(thumb_name, thumbnail)
