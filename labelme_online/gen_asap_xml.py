import os
import xml.dom.minidom

def generate_xml(xml_name, coordinates_all):
    """
        xml_name: full path name of asap xml (with extension)
        corrdinates_all: [(class_i, top_left(x,y), top_right(x,y), bottom_right(x,y), bottom_left)(x,y),]
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
    with open(xml_name, "w") as file:
        file.write(doc.toprettyxml(indent="\t"))