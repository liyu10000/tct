import os
import csv
import openslide
from PIL import Image, ImageDraw

from Config import *

class Patcher:
    def __init__(self, wsi_name, label_csv):
        self.wsi_name = wsi_name
        self.label_csv = label_csv
        self.meta = {}
        self.labels = {class_i:{} for class_i in CLASSES}
        self.read_meta()
        self.read_labels()

    def read_meta(self):
        slide = openslide.OpenSlide(self.wsi_name)
        level_count = slide.level_count
        self.meta['m'], self.meta['n'] = slide.level_dimensions[0]
        self.meta['mtop'], self.meta['ntop'] = slide.level_dimensions[level_count-1]
        self.meta['level_downsamples'] = slide.level_downsamples[level_count-1]
        self.meta['thumnail'] = slide.get_thumbnail((self.meta['mtop'], self.meta['ntop']))
        slide.close()

    def read_labels(self):
        """ read label information
        :output: {class_i: {(xmin, ymin, xmax, ymax):(xmin_z, ymin_z, xmax_z, ymax_z)}}
        """
        def zoom_out_labels():
            """ resize the coordinates of labels to accommodate thumbnail image """
            labels_new = {class_i:{} for class_i in CLASSES}
            for class_i, boxes in self.labels.items():
                for box in boxes:
                    box_z = (int(box[0]/self.meta['level_downsamples']),
                             int(box[1]/self.meta['level_downsamples']),
                             int(box[2]/self.meta['level_downsamples']),
                             int(box[3]/self.meta['level_downsamples']))
                    self.labels[class_i][box] = box_z

        if self.label_csv is None:
            return
        with open(self.label_csv) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for tokens in csv_reader:
                # skip first header
                if tokens[0] == "x_y":
                    continue
                x, y = tokens[0].split('_')
                x, y = int(x), int(y)
                class_i = tokens[3]
                # class_i, det = tokens[3], float(tokens[4])
                xmin, ymin = int(float(tokens[5])), int(float(tokens[6]))
                xmax, ymax = int(float(tokens[7])), int(float(tokens[8]))
                # box = (det, (x+xmin, y+ymin, x+xmax, y+ymax))
                box = (x+xmin, y+ymin, x+xmax, y+ymax)
                self.labels[class_i][box] = None
        zoom_out_labels()
                  

    def get_meta(self):
        return self.meta


    def get_labels(self):
        return self.labels

    def set_labels(self, labels):
        self.labels = labels


    def patch_label(self, classes):
        patched_image = self.meta['thumnail']
        draw = ImageDraw.Draw(patched_image)
        for class_i in classes:
            for box,box_z in self.labels[class_i].items():
                draw.rectangle(xy=box_z, fill=COLOURS[class_i], outline=COLOURS[class_i])
        # patched_image.show()
        return patched_image


if __name__ == "__main__":
    wsi_name = "res/test.tif"
    label_csv = "res/test_clas.csv"
    patcher = Patcher(wsi_name, label_csv)
    patcher.patch_label(CLASSES)
    labels = patcher.get_labels()
