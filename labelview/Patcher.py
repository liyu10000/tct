import os
import csv
import xml.dom.minidom
import openslide
from copy import copy
from PIL import Image, ImageFilter, ImageDraw
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed

from Config import cfg

class Patcher:
    def __init__(self, wsi_file, label_file):
        self.wsi_file = wsi_file
        self.label_file = label_file
        self.meta = {}
        self.labels = {class_i:{} for class_i in cfg.CLASSES}
        self.read_meta()
        self.read_labels()

    def read_meta(self):
        slide = openslide.OpenSlide(self.wsi_file)
        level_count = slide.level_count
        self.meta['m'], self.meta['n'] = slide.level_dimensions[0]
        self.meta['mtop'], self.meta['ntop'] = slide.level_dimensions[level_count-1]
        self.meta['level_downsamples'] = slide.level_downsamples[level_count-1]
        self.meta['thumbnail'] = slide.get_thumbnail((self.meta['mtop'], self.meta['ntop']))
        self.meta['thumbnail_blur'] = self.meta['thumbnail'].filter(ImageFilter.GaussianBlur(radius=16))
        slide.close()

    def read_labels(self):
        """ read label information
        :output: {class_i: {(xmin, ymin, xmax, ymax):(xmin_z, ymin_z, xmax_z, ymax_z)}}
        """
        def zoom_out_labels():
            """ resize the coordinates of labels to accommodate thumbnail image """
            for class_i, boxes in self.labels.items():
                for box in boxes:
                    box_z = (int(box[0]/self.meta['level_downsamples']),
                             int(box[1]/self.meta['level_downsamples']),
                             int(box[2]/self.meta['level_downsamples']),
                             int(box[3]/self.meta['level_downsamples']))
                    self.labels[class_i][box] = box_z

        def read_csv():
            with open(self.label_file) as csv_file:
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

        def read_xml():
            DOMTree = xml.dom.minidom.parse(self.label_file)
            collection = DOMTree.documentElement
            annotations = collection.getElementsByTagName("Annotation")
            for annotation in annotations:
                if not annotation.getAttribute("Color") in cfg.CONVERT:
                    continue
                coordinates = annotation.getElementsByTagName("Coordinate")
                # read (x, y) coordinates
                x_coords = [float(coordinate.getAttribute("X")) for coordinate in coordinates]
                y_coords = [float(coordinate.getAttribute("Y")) for coordinate in coordinates]
                xmin, ymin = int(min(x_coords)), int(min(y_coords))
                xmax, ymax = int(max(x_coords)), int(max(y_coords))
                box = (xmin, ymin, xmax, ymax)
                self.labels[cfg.CONVERT[annotation.getAttribute("Color")]][box] = None

        if self.label_file is None:
            return
        elif self.label_file.endswith(".csv"):
            read_csv()
        elif self.label_file.endswith(".xml"):
            read_xml()
        zoom_out_labels()
    

    def write_labels(self, label_file):
        doc = xml.dom.minidom.Document()
        ASAP_Annotations = doc.createElement("ASAP_Annotations")
        doc.appendChild(ASAP_Annotations)
        Annotations = doc.createElement("Annotations")
        ASAP_Annotations.appendChild(Annotations)
        AnnotationGroups = doc.createElement("AnnotationGroups")
        ASAP_Annotations.appendChild(AnnotationGroups)
        i = 0  # record the number of annotation (label)
        for class_i,boxes in self.labels.items():
            if class_i not in cfg.COLOURS:  # "DELETED!!!"
                continue
            for box in boxes:
                Annotation = doc.createElement("Annotation")
                Annotation.attributes["Color"] = cfg.COLOURS[class_i]
                Annotation.attributes["PartOfGroup"] = "None"
                Annotation.attributes["Type"] = "Polygon"
                Annotation.attributes["Name"] = "Annotation " + str(i)
                Annotations.appendChild(Annotation)
                i += 1

                Coordinates = doc.createElement("Coordinates")
                Annotation.appendChild(Coordinates)
                vertices = [(box[0],box[1]), (box[2],box[1]), (box[2],box[3]), (box[0],box[3])]
                for j in range(4):
                    Coordinate = doc.createElement("Coordinate")
                    Coordinate.attributes["X"] = str(vertices[j][0])
                    Coordinate.attributes["Y"] = str(vertices[j][1])
                    Coordinate.attributes["Order"] = str(j)
                    Coordinates.appendChild(Coordinate)
        with open(os.path.join(label_file), "w") as file:
            file.write(doc.toprettyxml(indent="\t"))


    def get_meta(self):
        return self.meta


    def get_labels(self):
        return self.labels

    def set_labels(self, labels):
        self.labels = labels


    def patch_label(self, classes):
        """ patch label boxes of choosen classes on thumbnail image
        :param classes: choosen label classes to patch
        :return: thumbnail image with label boxes patched
        """
        patched_image = copy(self.meta['thumbnail'])
        draw = ImageDraw.Draw(patched_image)
        for class_i in classes:
            for box,box_z in self.labels[class_i].items():
                draw.rectangle(xy=box_z, fill=cfg.COLOURS[class_i], outline=cfg.COLOURS[class_i])
        # patched_image.show()
        return patched_image

    def patch_label_mini(self, labels):
        patched_image = copy(self.meta["thumbnail_blur"])
        draw = ImageDraw.Draw(patched_image)
        for class_i,boxes in labels.items():
            for box,box_z in boxes.items():
                draw.rectangle(xy=box_z, fill=cfg.COLOURS[class_i], outline=cfg.COLOURS[class_i])
        # patched_image.show()
        return patched_image


    def batch_process(self, images_pre):
        """ batch cut images
        :param images_pre: [[class_i,(xmin,ymin,xmax,ymax),((xmin_z,ymin_z),(xmax_z,ymax_z))],]
        :return: [[class_i,(xmin,ymin,xmax,ymax),image],]
        """
        images = []
        slide = openslide.OpenSlide(self.wsi_file)
        for image_i in images_pre:
            image = slide.read_region(image_i[2][0], 0, image_i[2][1]).convert("RGB")
            images.append([image_i[0], image_i[1], image])
        slide.close()
        return images

    def crop_images(self, labels, N=2, batch_size=100):
        """ crop cell images from kfb/tif
        :param labels: {class_i: {(xmin, ymin, xmax, ymax): (xmin_z, ymin_z, xmax_z, ymax_z),},}
        :param N: the times of image size over cell (label box) size
        :return: [[class_i,(xmin, ymin, xmax, ymax),image],]
        """
        # prepare label coordinates for batch cut
        images_pre = []
        for class_i,boxes in labels.items():
            for box in boxes:
                x, y = box[0], box[1]
                w, h = box[2]-box[0], box[3]-box[1]
                x_cut, y_cut = int(x+(1-N)*w/2), int(y+(1-N)*h/2)
                w_cut, h_cut = int(N*w), int(N*h)
                images_pre.append([class_i, box, ((x_cut,y_cut),(w_cut,h_cut))])

        # cut images in batches
        executor = ProcessPoolExecutor(max_workers=cpu_count() - 4)
        tasks = []
        for i in range(0, len(images_pre), batch_size):
            tasks.append(executor.submit(self.batch_process, images_pre[i:i+batch_size]))

        # collect results
        images = []
        # job_count = len(tasks)
        for future in as_completed(tasks):
            result = future.result()  # get the returning result from calling fuction
            images.extend(result)
            # job_count -= 1
            # print("One Job Done, Rest Job Count: %s" % (job_count))

        return images


if __name__ == "__main__":
    wsi_file = "res/test.tif"
    label_file = "res/test_clas.csv"
    patcher = Patcher(wsi_file, label_file)
    # patcher.patch_label(cfg.CLASSES)
    labels = patcher.get_labels()
    # sub_labels = {}
    # patcher.patch_label_mini(sub_labels)
    patcher.crop_images(labels)
