import xml.etree.ElementTree as ET

template_file = "template_basic.xml"

tree = ET.parse(template_file)
root = tree.getroot()

print("\nTEMPLATE CARGADO\n")

track_count = 0

for node in root.findall(".//obj[@class='MListNode']"):

    name_tag = node.find("./string[@name='Name']")

    if name_tag is None:
        continue

    name = name_tag.attrib["value"]

    if name == "Automation":
        continue

    track_count += 1

print("Total tracks detectados:", track_count)