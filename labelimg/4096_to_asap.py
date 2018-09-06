"""
This will be used for the conversion of labelimg 4096 xmls to asap xmls.
Data source: stage2, local labelimg
"""

import os
import xml.dom.minidom

classes = {'AGC2': '#ff557f', 'ACTINO': '#55aa00', 'LSIL': '#005500', 'AGC3': '#ff55ff', 
           'EC': '#aa55ff', 'GEC': '#aa5500', 'HSIL': '#aa0000', 'AGC1': '#ff5500', 
           'SCC': '#0055ff', 'SC': '#aa00ff', 'ADC': '#aa557f', 'FUNGI': '#00aa00', 
           'CC': '#00aaff', 'ASCH': '#aa007f', 'TRI': '#00aa7f', 'MC': '#000000', 
           'RC': '#ff0000', 'VIRUS': '#55aa7f', 'ASCUS': '#00557f', 'NORMAL': '#ffffff'}


def scan_files(directory, prefix=None, postfix=None):
    files_list = []
    for root, sub_dirs, files in os.walk(directory):
        for special_file in files:
            if postfix:
                if special_file.endswith(postfix):
                    files_list.append(os.path.join(root, special_file))
            elif prefix:
                if special_file.startswith(prefix):
                    files_list.append(os.path.join(root, special_file))
            else:
                files_list.append(os.path.join(root, special_file))
    return files_list


def collect(xmls):
    def collect_i(xml_i):
        """
        :params xml_i: indivisual labelimg xml_i: "path/to/x_y.xml"
        :return: [(class_i, x, y, w, h),]
        """
        coordinates = []
        DOMTree = xml.dom.minidom.parse(xml_i)
        x4096, y4096 = os.path.splitext(os.path.basename(xml_i))[0].split("_")
        x4096, y4096 = int(x4096), int(y4096)
        collection = DOMTree.documentElement
        objects = collection.getElementsByTagName("object")
        for object_i in objects:
            name = object_i.getElementsByTagName("name")[0]
            class_i = name.firstChild.nodeValue
            xmin = int(object_i.getElementsByTagName("xmin")[0].firstChild.nodeValue)
            ymin = int(object_i.getElementsByTagName("ymin")[0].firstChild.nodeValue)
            xmax = int(object_i.getElementsByTagName("xmax")[0].firstChild.nodeValue)
            ymax = int(object_i.getElementsByTagName("ymax")[0].firstChild.nodeValue)
            coordinates.append((class_i, xmin+x4096, ymin+y4096, xmax-xmin, ymax-ymin))
        return coordinates

    coordinates = []
    for xml_i in xmls:
        coords = collect_i(xml_i)
        coordinates += coords
    return coordinates 


def xml_write(tif, coords, path_out):
    """
    write coords info into asap xml: "path_out/tif.xml"
    :params tif: tif basename, without extension
    :params coords: [(class_i, x, y, w, h),]
    :params path_out: save path of xml file
    """
    def convert_coords(coords):
        """
        convert coordinates, for ease of writing
        :params coords: [(class_i, x, y, w, h),]
        :return: [(class_i, top_left, top_right, bottom_right, bottom_left),]
        """
        coords_new = []
        for box in coords:
            top_left = (box[1], box[2])
            top_right = (box[1]+box[3], box[2])
            bottom_right = (box[1]+box[3], box[2]+box[4])
            bottom_left = (box[1], box[2]+box[4])
            coords_new.append((box[0], top_left, top_right, bottom_right, bottom_left))
        return coords_new

    doc = xml.dom.minidom.Document()
    ASAP_Annotations = doc.createElement("ASAP_Annotations")
    doc.appendChild(ASAP_Annotations)
    Annotations = doc.createElement("Annotations")
    ASAP_Annotations.appendChild(Annotations)
    AnnotationGroups = doc.createElement("AnnotationGroups")
    ASAP_Annotations.appendChild(AnnotationGroups)
    coords = convert_coords(coords)
    for i, box in enumerate(coords):
        Annotation = doc.createElement("Annotation")
        Annotation.attributes["Color"] = classes[box[0]]
        Annotation.attributes["PartOfGroup"] = "None"
        Annotation.attributes["Type"] = "Polygon"
        Annotation.attributes["Name"] = "Annotation " + str(i)
        Annotations.appendChild(Annotation)

        Coordinates = doc.createElement("Coordinates")
        Annotation.appendChild(Coordinates)
        for j in range(4):
            Coordinate = doc.createElement("Coordinate")
            Coordinate.attributes["X"] = str(box[j+1][0])
            Coordinate.attributes["Y"] = str(box[j+1][1])
            Coordinate.attributes["Order"] = str(j)
            Coordinates.appendChild(Coordinate)
    with open(os.path.join(path_out, tif+".xml"), "w") as file:
        file.write(doc.toprettyxml(indent="\t"))    

def convert(tif, path_in, path_out):
    """
    collect coordinates info of single tif and write into an asap xml file
    :params tif: tif basename
    :params path_in: the file path to labelimg xmls
    :params path_out: save path of result asap xml
    """
    xmls = scan_files(path_in, postfix=".xml")
    coords = collect(xmls)
    xml_write(tif, coords, path_out)


def main(path_in, path_out):
    users = os.listdir(path_in)
    for user in users:
        tifs = os.listdir(os.path.join(path_in, user))
        for tif in tifs:
            user_tif_path_in = os.path.join(path_in, user, tif)
            user_tif_path_out = os.path.join(path_out, user)
            os.makedirs(user_tif_path_out, exist_ok=True)
            convert(tif, user_tif_path_in, user_tif_path_out)
            print("processed ", tif)
        print("finished ", user)


if __name__ == "__main__":
    path_in = "/media/tsimage001/Elements/data0/labeled/jpg4096"
    path_out = "/media/tsimage001/Elements/data0/labeled/xml4096"
    main(path_in, path_out)
