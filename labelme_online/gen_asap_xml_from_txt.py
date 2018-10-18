import os
import xml.dom.minidom


def generate_xml(xml_name, coordinates_all):
    """
    :params xml_name: full path name of asap xml (with extension)
    :params coordinates_all: [(class_i, top_left(x,y), top_right(x,y), bottom_right(x,y), bottom_left)(x,y)),]
    """
    classes = {'AGC2': '#ff557f', 'ACTINO': '#55aa00', 'LSIL': '#005500', 'AGC3': '#ff55ff', 
           'EC': '#aa55ff', 'GEC': '#aa5500', 'HSIL': '#aa0000', 'AGC1': '#ff5500', 
           'SCC': '#0055ff', 'SC': '#aa00ff', 'ADC': '#aa557f', 'FUNGI': '#00aa00', 
           'CC': '#00aaff', 'ASCH': '#aa007f', 'TRI': '#00aa7f', 'MC': '#000000', 
           'RC': '#ff0000', 'VIRUS': '#55aa7f', 'ASCUS': '#00557f'}
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
    with open(xml_name, "w") as file:
        file.write(doc.toprettyxml(indent="\t"))

def collect_coordinates(txt_dir):
    """
    collects coordinates from stage2_online annotation files.
    content format of txt in txt_dir
    x,y,w,h,class_i,jpg_path,jpg_x,jpg_y
    :return: tif_coords:{tif: [(class_i, top_left(x,y), top_right(x,y), bottom_right(x,y), bottom_left)(x,y)),]}
    """
    txts = os.listdir(txt_dir)
    boxes = []
    for txt in txts:
        with open(os.path.join(txt_dir, txt), 'r') as f:
            for line in f:
                tokens = line.split(',')
                x, y = int(tokens[0]) + int(tokens[-2]), int(tokens[1]) + int(tokens[-1])
                w, h = int(tokens[2]), int(tokens[3])
                class_i = tokens[4]  #MC, ASCUS like
                boxes.append((class_i, (x,y), (x+w,y), (x+w,y+h), (x,y+h)))
    return {os.path.basename(txt_dir):boxes}

def main(txt_path, xml_path):
    tif_coords = {}
    for txt_dir in os.listdir(txt_path):
        tif_coords.update(collect_coordinates(os.path.join(txt_path, txt_dir)))
    for tif, coords in tif_coords.items():
        xml_name = os.path.join(xml_path, tif+".xml")
        generate_xml(xml_name, coords)
        print("processed {}".format(tif))


if __name__ == "__main__":
    jpg_path = "/home/sakulaki/yolo-yuli/xxx/data_unchecked_20180922"
    xml_path = "/home/sakulaki/yolo-yuli/xxx/data_20180922/all"
    # main(jpg_path, xml_path)

    # # replace blank space with '-'
    # files = os.listdir(xml_path)
    # for f in files:
    #     if ' ' in f:
    #         os.rename(os.path.join(xml_path, f), os.path.join(xml_path, f.replace(' ', '-')))