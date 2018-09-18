#coding=utf-8  

from xml.dom.minidom import parse
import xml.dom.minidom

DOMTree = xml.dom.minidom.parse("E:\\liyu\\files\\2017-10-09 15_56_34.xml")
collection = DOMTree.documentElement

colorCounts = {	"#000000":0,
			"#aa0000":0,
			"#aa007f":0,
			"#aa00ff":0,
			"#ff0000":0,
			"#005500":0,
			"#00557f":0,
			"#0055ff":0,
			"#aa5500":0,
			"#aa557f":0,
			"#aa55ff":0,
			"#ff5500":0,
			"#ff557f":0,
			"#ff55ff":0,
			"#00aa00":0,
			"#00aa00":0,
			"#00aa7f":0,
			"#00aaff":0,
			"#55aa00":0,
			"#55aa7f":0}

annotations = collection.getElementsByTagName("Annotation")
for annotation in annotations:
	if annotation.getAttribute("Color") == "#005500":
		print("Color: " + annotation.getAttribute("Color"))
	colorCounts[annotation.getAttribute("Color")] += 1
	
print(colorCounts)