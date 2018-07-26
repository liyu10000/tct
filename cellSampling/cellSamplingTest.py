import os

import openslide
# import numpy
import scipy.misc

from xml.dom.minidom import parse
import xml.dom.minidom


# open tiff image
tif_file = "C:\\liyu\\files\\tiff\\large.tif"
slide = openslide.OpenSlide(tif_file)

# open xml file
xml_file = "C:\\liyu\\files\\tiff\\large.xml"
DOMTree = xml.dom.minidom.parse(xml_file)
collection = DOMTree.documentElement
annotations = collection.getElementsByTagName("Annotation")

for annotation in annotations:
    coordinates = annotation.getElementsByTagName("Coordinate")

    # read (x, y) coordinates
    x_coords = []
    y_coords = []
    for coordinate in coordinates:
        x_coords.append(float(coordinate.getAttribute("X")))
        y_coords.append(float(coordinate.getAttribute("Y")))

    # get mininum-area-bounding-rectangle
    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)

    x = int(1.5*x_min - 0.5*x_max)
    y = int(1.5*y_min - 0.5*y_max)
    x_size = int(2*(x_max - x_min))
    y_size = int(2*(y_max - y_min))

    cell = slide.read_region((x, y), 0, (x_size, y_size))
    # cell_array = numpy.array(cell)
    cell = cell.convert("RGB")
    scipy.misc.imsave("C:\\liyu\\files\\tiff\\cells\\"+annotation.getAttribute("Name")+".jpeg", cell)


slide.close()
