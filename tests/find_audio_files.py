import xml.etree.ElementTree as ET

tree = ET.parse("template_basic.xml")
root = tree.getroot()

print("\nARCHIVOS DE AUDIO REFERENCIADOS:\n")

for string in root.findall(".//string"):

    value = string.attrib.get("value", "")

    if value.lower().endswith((".wav", ".aif", ".aiff")):
        print(value)