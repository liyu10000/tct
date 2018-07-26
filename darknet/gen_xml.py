import os
import xml.dom.minidom
import xml.etree.ElementTree as ET


class Xml:
    def __init__(self, filename, save_path, points_xy, labels, size):
        """
        filename: basename (without file extension)
        points_xy: {(x, y): [i,]}
        labels: {i: (x_min, x_max, y_min, y_max, color)}
        """
        self.filename = filename
        self.save_path = save_path
        self.points_xy = points_xy
        self.labels = labels
        self.size = size
        
    def gen_xml(self):
        for xy, label_indexs in self.points_xy.items():
            root = ET.Element("annotation")
            ET.SubElement(root, "folder").text = "folder"
            ET.SubElement(root, "filename").text = self.filename + "_" + str(xy[0]) + "_" + str(xy[1]) + ".jpg"
            ET.SubElement(root, "path").text = "path"

            source = ET.SubElement(root, "source")
            ET.SubElement(source, "database").text = "Unknown"

            size = ET.SubElement(root, "size")
            ET.SubElement(size, "width").text = str(self.size)
            ET.SubElement(size, "height").text = str(self.size)
            ET.SubElement(size, "depth").text = "3"

            ET.SubElement(root, "segmented").text = "0"
            
            for label_index in label_indexs:
                object = ET.SubElement(root, "object")
                ET.SubElement(object, "name").text = self.labels[label_index][4]
                ET.SubElement(object, "pose").text = "Unspecified"
                ET.SubElement(object, "truncated").text = "0"
                ET.SubElement(object, "difficult").text = "0"
                bndbox = ET.SubElement(object, "bndbox")
                label_xmin = self.labels[label_index][0]
                label_xmax = self.labels[label_index][1]
                label_ymin = self.labels[label_index][2]
                label_ymax = self.labels[label_index][3]
                label_xmin_new = label_xmin - xy[0]
                label_ymin_new = label_ymin - xy[1]
                label_xmax_new = label_xmax - xy[0]
                label_ymax_new = label_ymax - xy[1]
                if label_xmin <= xy[0] and xy[0]+self.size <= label_xmax:
                    label_xmin_new = 0
                    label_xmax_new = self.size
                if label_ymin <= xy[1] and xy[1]+self.size <= label_ymax:
                    label_ymin_new = 0
                    label_ymax_new = self.size
                ET.SubElement(bndbox, "xmin").text = str(label_xmin_new)
                ET.SubElement(bndbox, "ymin").text = str(label_ymin_new)
                ET.SubElement(bndbox, "xmax").text = str(label_xmax_new)
                ET.SubElement(bndbox, "ymax").text = str(label_ymax_new)

            raw_string = ET.tostring(root, "utf-8")
            reparsed = xml.dom.minidom.parseString(raw_string)
            file = open(os.path.join(self.save_path, self.filename + "_" + str(xy[0]) + "_" + str(xy[1]) + ".xml"), "w")
            file.write(reparsed.toprettyxml(indent="\t"))
            file.close()
            # tree = ET.ElementTree(root)
            # tree.write("test.xml")
        
