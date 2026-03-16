import os
import shutil
from lxml import etree as ET
from src.audio_event_builder import AudioEventBuilder

TEMPLATE = "templates/template_basic.xml"
STEMS_FOLDER = "stems"
OUTPUT = "output"
MEDIA_FOLDER = os.path.join(OUTPUT, "Media")

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

    renamed_files = []

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

            renamed_files.append((track, new_name))

    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(TEMPLATE, parser)
    root = tree.getroot()

    builder = AudioEventBuilder()

    print("\nCREANDO EVENTOS DE AUDIO:\n")

    pool = root.find(".//obj[@class='Pool']")

    if pool is None:

        print("Pool no encontrado. Creando Pool automáticamente.\n")

        pool = ET.Element(
            "obj",
            {
                "class": "Pool",
                "ID": "1000"
            }
        )

        root.append(pool)

    for track, filename in renamed_files:

        audio_file, audio_file_id = builder.create_audio_file(filename)
        pool.append(audio_file)

        clip, clip_id = builder.create_audio_clip(audio_file_id)
        pool.append(clip)

        event = builder.create_audio_event(clip_id)

        for string_node in root.findall(".//string"):

            value = string_node.attrib.get("value", "").upper()

            if value == track.upper():

                parent = string_node.getparent()

                events = parent.find(".//member[@name='Events']")

                if events is not None:
                    events.append(event)

                    print(filename, "→", track)

    os.makedirs(OUTPUT, exist_ok=True)

    output_xml = os.path.join(OUTPUT, "session.xml")

    tree.write(output_xml, pretty_print=True)

    print("\nSesión generada en:")
    print(output_xml)