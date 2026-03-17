from lxml import etree


def extract_tracks(root):
    """
    Extrae pistas válidas desde un XML de Cubase.

    Devuelve:
    dict[str, xml_node]
    """

    tracks = {}

    for node in root.xpath(".//obj[@class='MListNode']"):

        name_node = node.find("./string[@name='Name']")

        if name_node is None:
            continue

        name = name_node.get("value")

        if not name:
            continue

        name_lower = name.lower()

        # filtros para ignorar nodos que no son pistas reales
        ignore = [
            "standard panner",
            "archivo wave",
            "automation",
            "quick controls",
            "vst multitrack",
            "input filter",
            "eq",
            "stereo in"
        ]

        if name_lower in ignore:
            continue

        if name_lower.endswith(".wav"):
            continue

        if name_lower.startswith("audio "):
            continue

        tracks[name_lower] = node

    return tracks