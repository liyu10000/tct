import os
import xml.dom.minidom


classes = {'AGC2': '#ff557f', 'ACTINO': '#55aa00', 'LSIL': '#005500', 'AGC3': '#ff55ff', 
           'EC': '#aa55ff', 'GEC': '#aa5500', 'HSIL': '#aa0000', 'AGC1': '#ff5500', 
           'SCC': '#0055ff', 'SC': '#aa00ff', 'ADC': '#aa557f', 'FUNGI': '#00aa00', 
           'CC': '#00aaff', 'ASCH': '#aa007f', 'TRI': '#00aa7f', 'MC': '#000000', 
           'RC': '#ff0000', 'VIRUS': '#55aa7f', 'ASCUS': '#00557f', 
           'AGC2-3': '#ff557f', 'NORMAL': '#ffffff'}


def generate_xml(tif, coordinates_all, path_out):
    """
    :params tif: basename of tif (without extension)
    :params corrdinates_all: [(class_i, top_left, top_right, bottom_right, bottom_left),]
    :params path_out: xml save path
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
    with open(os.path.join(path_out, tif+".xml"), "w") as file:
        file.write(doc.toprettyxml(indent="\t"))


def collect_coords(tif_dir):
    """
    collect coordinates from single tif folder.
    tree view of tif_dir should be:
    tif_dir:
        class_0:
            tif_x_y_w_h.jpg
            ...
        class_1:
            tif_x_y_w_h.jpg
            ...
        ...
    :params tif_dir: tif directory path
    :return: coordinates: [(class_i, x, y, w, h),]
    """
    coords = []
    tif_classes = os.listdir(tif_dir)
    for class_i in tif_classes:
        tif_path_i = os.path.join(tif_dir, class_i)
        jpgs = os.listdir(tif_path_i)
        for jpg in jpgs:
            tokens = os.path.splitext(jpg)[0].rsplit('_', 4)
            x, y = int(tokens[1][1:]), int(tokens[2][1:])
            w, h = int(tokens[3][1:]), int(tokens[4][1:])
            coords.append((class_i, x, y, w, h))
    return coords


def convert_coords(coords):
    """
    convert coords from [(class_i, x, y, w, h),]
                   to [(class_i, top_left, top_right, bottom_right, bottom_left),]
    :params coords: [(class_i, x, y, w, h),]
    :return: [(class_i, top_left, top_right, bottom_right, bottom_left),]
    """
    return [(box[0], 
            (box[1], box[2]),
            (box[1]+box[3], box[2]),
            (box[1]+box[3], box[2]+box[4]),
            (box[1], box[2]+box[4]))
            for box in coords]


def main(path_in, path_out):
    """
    tree view of path_in:
    path_in:
        sub_dir1:
            tif_dir1:
                class_0:
                    tif_x_y_w_h.jpg
                    ...
                class_1:
                    tif_x_y_w_h.jpg
                    ...
    path_out should preserves the structure
    """
    sub_dirs = os.listdir(path_in)
    for sub_dir in sub_dirs:
        tifs = os.listdir(os.path.join(path_in, sub_dir))
        for tif in tifs:
            coords = collect_coords(os.path.join(path_in, sub_dir, tif))
            coords = convert_coords(coords)
            path_out_i = os.path.join(path_out, sub_dir)
            os.makedirs(path_out_i, exist_ok=True)
            generate_xml(tif, coords, path_out_i)
            print("generated", os.path.join(path_out_i, tif+".xml"))
        print("finished", sub_dir)


if __name__ == "__main__":
    path_in = ""
    path_out = ""
    main(path_in, path_out)