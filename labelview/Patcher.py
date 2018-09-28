import os
import csv
import openslide
from PIL import Image, ImageDraw


class Patcher:
    def __init__(self, wsi_name, label_csv):
        self.wsi_name = wsi_name
        self.label_csv = label_csv
        self.meta = {}
        self.labels_old = {}
        self.labels_new = {}
        # self.patched_images = {}
        self.read_meta()
        self.read_labels()
        self.convert_labels()

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
        :output: {class_i: [(p, (xmin, ymin, xmax, ymax)),]}
        """
        with open(self.label_csv) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for tokens in csv_reader:
                # skip first header
                if tokens[0] == "x_y":
                    continue
                x, y = tokens[0].split('_')
                x, y = int(x), int(y)
                class_i, det = tokens[3], float(tokens[4])
                xmin, ymin = int(float(tokens[5])), int(float(tokens[6]))
                xmax, ymax = int(float(tokens[7])), int(float(tokens[8]))
                box = (det, (x+xmin, y+ymin, x+xmax, y+ymax))
                if not class_i in self.labels_old:
                    self.labels_old[class_i] = [box,]
                else:
                    self.labels_old[class_i].append(box)

    def convert_labels(self):
        for class_i, boxes in self.labels_old.items():
            self.labels_new[class_i] = []
            for box in boxes:
                box_new = (box[0], (int(box[1][0]/self.meta['level_downsamples']),
                                    int(box[1][1]/self.meta['level_downsamples']),
                                    int(box[1][2]/self.meta['level_downsamples']),
                                    int(box[1][3]/self.meta['level_downsamples'])))
                self.labels_new[class_i].append(box_new)

    def get_meta(self):
        return self.meta

    def patch_label(self, classes):
        patched_image = self.meta['thumnail']
        draw = ImageDraw.Draw(patched_image)
        for class_i in classes:
            if not class_i in self.labels_new:
                continue
            for box in self.labels_new[class_i]:
                draw.rectangle(xy=box[1], fill=None, outline=225)
        # self.patched_images[tuple(classes)] = patched_image
        patched_image.show()
        return patched_image


if __name__ == "__main__":
    wsi_name = "C:\\tsimage\\tct\\labelview\\res\\test.tif"
    label_csv = "C:\\tsimage\\tct\\labelview\\res\\test_clas.csv"
    patcher = Patcher(wsi_name, label_csv)
    patcher.patch_label(["ASCH"])
