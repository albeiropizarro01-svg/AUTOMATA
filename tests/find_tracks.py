import xml.etree.ElementTree as ET

template_file = "template_basic.xml"

tree = ET.parse(template_file)
root = tree.getroot()

target_tracks = ["KICK", "SNARE", "LEAD VOCAL", "PAD"]

print("\nBUSCANDO PISTAS EN EL TEMPLATE\n")

for node in root.findall(".//obj[@class='MListNode']"):

    name_tag = node.find("./string[@name='Name']")

    if name_tag is None:
        continue

    name = name_tag.attrib["value"]

    if name.upper() in target_tracks:
        print("TRACK ENCONTRADA:", name)