from lxml import etree


def rename_tracks_safe(root, rename_map):
    """
    Renombra pistas de forma SEGURA y opcional.

    REGLAS:
    - Solo afecta MListNode (tracks reales)
    - Matching exacto (no substring)
    - No rompe template si no hay match

    rename_map:
    {
        "kick": "KICK MAIN",
        "snare": "SNARE TOP"
    }
    """

    if not rename_map:
        return root

    for node in root.xpath(".//obj[@class='MListNode']"):

        name_node = node.find("./string[@name='Name']")

        if name_node is None:
            continue

        name = name_node.get("value")

        if not name:
            continue

        name_lower = name.lower().strip()

        # matching exacto
        if name_lower in rename_map:
            name_node.set("value", rename_map[name_lower])

    return root