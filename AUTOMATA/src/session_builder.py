import os
import shutil
import xml.etree.ElementTree as ET

TEMPLATE = "templates/template_basic.xml"
STEMS_FOLDER = "stems"
OUTPUT = "output"
MEDIA_FOLDER = os.path.join(OUTPUT, "Media")

# ------------------------------------------------
# CLASIFICACION INTELIGENTE
# ------------------------------------------------

KEYWORDS = {
    "kick": "KICK",
    "snare": "SNARE",
    "clap": "SNARE",
    "hat": "HIHAT",
    "hihat": "HIHAT",
    "808": "SUB-BASS",
    "bass": "BASS",
    "sub": "SUB-BASS",
    "pad": "AMBIENT",
    "piano": "KEYS",
    "lead": "LEAD VOCAL",
    "vocal": "LEAD VOCAL",
    "vox": "LEAD VOCAL",
}

def classify_stem(filename):

    name = filename.lower()

    for keyword, track in KEYWORDS.items():
        if keyword in name:
            return track

    return None


# ------------------------------------------------
# GENERADOR PRINCIPAL
# ------------------------------------------------

def generate_session():

    print("\n=== STEM SESSION BUILDER ===\n")

    stems = []

    for file in os.listdir(STEMS_FOLDER):

        if file.lower().endswith(".wav"):
            stems.append(file)

    print("STEMS ENCONTRADOS:\n")

    for s in stems:
        print("-", s)

    matches = {}

    for stem in stems:

        track = classify_stem(stem)

        if track is None:
            continue

        if track not in matches:
            matches[track] = []

        matches[track].append(stem)

    print("\nMATCHES:\n")

    for track in matches:
        for stem in matches[track]:
            print(stem, "→", track)

    os.makedirs(MEDIA_FOLDER, exist_ok=True)

    renamed_files = {}

    for track in matches:

        stems_list = matches[track]

        for i, stem in enumerate(stems_list):

            if i == 0:
                new_name = f"{track}.wav"
            else:
                new_name = f"{track}_{i+1}.wav"

            src = os.path.join(STEMS_FOLDER, stem)
            dst = os.path.join(MEDIA_FOLDER, new_name)

            shutil.copy(src, dst)

            renamed_files[track] = new_name

    tree = ET.parse(TEMPLATE)
    root = tree.getroot()

    print("\nASIGNANDO AUDIO AL TEMPLATE:\n")

    for node in root.findall(".//obj[@class='FNPath']"):

        name_tag = node.find("./string[@name='Name']")

        if name_tag is None:
            continue

        track_name = name_tag.attrib["value"]

        if track_name in renamed_files:

            name_tag.attrib["value"] = renamed_files[track_name]

            print(renamed_files[track_name], "→", track_name)

    output_xml = os.path.join(OUTPUT, "session.xml")

    tree.write(output_xml)

    print("\nSesión generada en:")
    print(output_xml)