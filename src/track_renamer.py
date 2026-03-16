from lxml import etree


def rename_tracks(xml_root, matches):

    # mapa: tipo de pista → nuevo nombre
    rename_map = {}

    counters = {}

    for stem, track_type in matches:

        track_type = track_type.upper()

        if track_type not in counters:
            counters[track_type] = 1
        else:
            counters[track_type] += 1

        if counters[track_type] == 1:
            new_name = track_type
        else:
            new_name = f"{track_type}_{counters[track_type]}"

        rename_map[track_type.lower()] = new_name

    # buscar todos los nombres de pista
    for node in xml_root.xpath('//string[@name="Name"]'):

        name = node.get("value")

        if not name:
            continue

        name_lower = name.lower()

        for key in rename_map:

            if key in name_lower:

                node.set("value", rename_map[key])

    return xml_root