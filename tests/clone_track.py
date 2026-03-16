import xml.etree.ElementTree as ET
import copy

template_file = "template_basic.xml"

tree = ET.parse(template_file)
root = tree.getroot()

track_nodes = {}

for node in root.findall(".//obj[@class='MListNode']"):

    name_tag = node.find("./string[@name='Name']")

    if name_tag is None:
        continue

    name = name_tag.attrib["value"]

    if name == "Automation":
        continue

    track_nodes[name] = node


print("\nCLONANDO PISTA...\n")

original = track_nodes["LEAD VOCAL"]

clone = copy.deepcopy(original)

name_tag = clone.find("./string[@name='Name']")
name_tag.attrib["value"] = "LEAD VOCAL 2"

print("Original:", original.find("./string[@name='Name']").attrib["value"])
print("Clon:", clone.find("./string[@name='Name']").attrib["value"])