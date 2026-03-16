import xml.etree.ElementTree as ET

tree = ET.parse("template_basic.xml")
root = tree.getroot()

print("\nEVENTOS DE AUDIO ENCONTRADOS:\n")

for event in root.findall(".//obj[@class='MAudioTrackEvent']"):

    file_tag = event.find(".//string[@name='Name']")

    if file_tag is not None:
        print(file_tag.attrib["value"])