from lxml import etree


def extract_tracks(template_path):

    tree = etree.parse(template_path)
    root = tree.getroot()

    tracks = {}

    # buscar todos los nodos que contienen nombres
    for node in root.xpath('//string[@name="Name"]'):

        name = node.get("value")

        if not name:
            continue

        name_lower = name.lower()

        # ignorar cosas que no son pistas
        ignore = [
            "standard panner",
            "archivo wave",
            "automation",
            "quick controls"
        ]

        if name_lower in ignore:
            continue

        tracks[name_lower] = name

    return tracks