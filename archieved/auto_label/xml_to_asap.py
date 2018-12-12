import os
import xml.dom.minidom

classes = {'AGC2': '#ff557f', 'ACTINO': '#55aa00', 'LSIL': '#005500', 'AGC3': '#ff55ff', 
           'EC': '#aa55ff', 'GEC': '#aa5500', 'HSIL': '#aa0000', 'AGC1': '#ff5500', 
           'SCC': '#0055ff', 'SC': '#aa00ff', 'ADC': '#aa557f', 'FUNGI': '#00aa00', 
           'CC': '#00aaff', 'ASCH': '#aa007f', 'TRI': '#00aa7f', 'MC': '#000000', 
           'RC': '#ff0000', 'VIRUS': '#55aa7f', 'ASCUS': '#00557f'}


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


def collect_labels_from_xml(xml_file):
    """
        return: (x, y), [(class_i, xmin, ymin, xmax, ymax),]
    """
    basename = os.path.splitext(os.path.basename(xml_file))[0]
    x_y = [int(i) for i in basename.split("_")]
    coordinates = []
    try:
        DOMTree = xml.dom.minidom.parse(xml_file)
    except:
        print("empty xml")
        return (-1, -1), []
    collection = DOMTree.documentElement
    objects = collection.getElementsByTagName("object")
    for object in objects:
        name = object.getElementsByTagName("name")[0]
        class_i = name.firstChild.nodeValue
        xmin = int(object.getElementsByTagName("xmin")[0].firstChild.nodeValue)
        ymin = int(object.getElementsByTagName("ymin")[0].firstChild.nodeValue)
        xmax = int(object.getElementsByTagName("xmax")[0].firstChild.nodeValue)
        ymax = int(object.getElementsByTagName("ymax")[0].firstChild.nodeValue)
        coordinates.append((class_i, xmin, ymin, xmax, ymax))
    return tuple(x_y), coordinates


def convert_coordinates(x_y, coordinates):
    """
        return: [(class_i, top_left, top_right, bottom_right, bottom_left),]
    """
    if x_y == (-1, -1):
        return []
    coordinates_asap = []
    for box in coordinates:
        top_left = (x_y[0]+box[1], x_y[1]+box[2])
        top_right = (x_y[0]+box[3], x_y[1]+box[2])
        bottom_left = (x_y[0]+box[1], x_y[1]+box[4])
        bottom_right = (x_y[0]+box[3], x_y[1]+box[4])
        coordinates_asap.append((box[0], top_left, top_right, bottom_right, bottom_left))
    return coordinates_asap


def generate_xml(tif_name, coordinates_all):
    """
        tif_name: full path name of tif_name (with extension)
        corrdinates_all: [(class_i, top_left, top_right, bottom_right, bottom_left),]
    """
    doc = xml.dom.minidom.Document()
    ASAP_Annotations = doc.createElement("ASAP_Annotations")
    doc.appendChild(ASAP_Annotations)
    Annotations = doc.createElement("Annotations")
    ASAP_Annotations.appendChild(Annotations)
    AnnotationGroups = doc.createElement("AnnotationGroups")
    ASAP_Annotations.appendChild(AnnotationGroups)
    for i, box in enumerate(coordinates_all):
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
    with open(tif_name, "w") as file:
        file.write(doc.toprettyxml(indent="\t"))


def gen_asap_xml(tif_name, path_in):
    xmls = scan_files(path_in, postfix=".xml")
    coordinates_all = []
    for xml in xmls:
        x_y, coordinates = collect_labels_from_xml(xml)
        coordinates_asap = convert_coordinates(x_y, coordinates)
        coordinates_all += coordinates_asap
    generate_xml(tif_name, coordinates_all)


if __name__ == "__main__":
    path_in = "C:\\Users\\liyud\\Desktop\\yantian_jpg\\2018-07-29-00_43_42_segment"
    tif_name = "C:\\Users\\liyud\\Desktop\\yantian_jpg\\2018-07-29-00_43_42_segment.xml"
    gen_asap_xml(tif_name, path_in)
