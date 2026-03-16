import xml.etree.ElementTree as ET

file_path = "template_basic.xml"

tree = ET.parse(file_path)
root = tree.getroot()

print("\nESTRUCTURA REAL DEL TEMPLATE:\n")

for tracklist in root.findall(".//obj[@class='MTrackList']"):

    name_tag = tracklist.find("./string[@name='Name']")

    if name_tag is None:
        continue

    folder = name_tag.attrib["value"]

    if folder == "Automation":
        continue

    print(f"\nFOLDER: {folder}")

    for node in tracklist.findall(".//obj[@class='MListNode']"):

        track_name = node.find("./string[@name='Name']")

        if track_name is None:
            continue

        name = track_name.attrib["value"]

        if name == "Automation":
            continue

        # detectar grupo
        if name == folder:
            print(f"   GROUP: {name}")
        else:
            print(f"   TRACK: {name}")