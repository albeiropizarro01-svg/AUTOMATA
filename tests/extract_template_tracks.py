import xml.etree.ElementTree as ET

template_file = "template_basic.xml"

tree = ET.parse(template_file)
root = tree.getroot()

tracks = []

for node in root.findall(".//obj[@class='MListNode']"):

    name_tag = node.find("./string[@name='Name']")

    if name_tag is None:
        continue

    name = name_tag.attrib["value"]

    if name == "Automation":
        continue

    tracks.append(name)

print("\nTRACKS DEL TEMPLATE:\n")

for t in tracks:
    print("-", t)