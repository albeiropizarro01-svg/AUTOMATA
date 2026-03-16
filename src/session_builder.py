from lxml import etree
from pathlib import Path
import uuid
import copy


class SessionBuilder:

    def __init__(self, template_path, matches, output_path):

        self.template_path = Path(template_path)
        self.matches = matches
        self.output_path = Path(output_path)

        self.tree = etree.parse(str(self.template_path))
        self.root = self.tree.getroot()

        self.tracks = self.extract_tracks()

    def generate_id(self):
        return str(uuid.uuid4().int >> 64)

    # ---------------------------------------
    # DETECTAR PISTAS
    # ---------------------------------------

    def extract_tracks(self):

        tracks = {}

        for node in self.root.xpath('//string[@name="Name"]'):

            name = node.get("value")

            if not name:
                continue

            name_lower = name.lower()

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

    # ---------------------------------------
    # OBTENER EVENTO BASE
    # ---------------------------------------

    def get_template_event(self):

        event = self.root.find(".//obj[@class='MAudioEvent']")

        if event is None:
            raise Exception("Template no contiene MAudioEvent")

        return event

    # ---------------------------------------
    # CLONAR EVENTO
    # ---------------------------------------

    def clone_event(self):

        template_event = self.get_template_event()

        new_event = copy.deepcopy(template_event)

        new_event.set("ID", str(self.generate_id()))

        return new_event

    # ---------------------------------------
    # ACTUALIZAR RUTAS DE AUDIO
    # ---------------------------------------

    def update_audio_paths(self, event, filename):

        base = filename.replace(".wav", "")

        # actualizar descripción
        desc = event.find(".//string[@name='Description']")
        if desc is not None:
            desc.set("value", base)

        # actualizar nombre del clip
        clip_name = event.find(".//obj[@class='PAudioClip']/string[@name='Name']")
        if clip_name is not None:
            clip_name.set("value", base)

        # FNPath
        fn_name = event.find(".//obj[@class='FNPath']/string[@name='Name']")
        if fn_name is not None:
            fn_name.set("value", filename)

        fn_path = event.find(".//obj[@class='FNPath']/string[@name='Path']")
        if fn_path is not None:
            fn_path.set("value", "Media")

        # FPath dentro del AudioCluster
        fpath_name = event.find(".//obj[@name='FPath']/string[@name='Name']")
        if fpath_name is not None:
            fpath_name.set("value", filename)

        fpath_path = event.find(".//obj[@name='FPath']/string[@name='Path']")
        if fpath_path is not None:
            fpath_path.set("value", "Media")

    # ---------------------------------------
    # BUSCAR PISTA
    # ---------------------------------------

    def find_best_track(self, track_type):

        track_type = track_type.lower()

        synonyms = {
            "ambient": ["pad"],
            "hihat": ["hat"],
            "keys": ["piano", "keys"],
            "snare": ["snare", "clap"],
            "kick": ["kick"],
            "bass": ["bass", "808"]
        }

        words = synonyms.get(track_type, [track_type])

        for track in self.tracks:

            for w in words:

                if w in track:
                    return self.tracks[track]

        return None

    # ---------------------------------------
    # INSERTAR EVENTO
    # ---------------------------------------

    def insert_event(self, track_node, event):

        parent = track_node.getparent()

        if parent is not None:
            parent.append(event)

    # ---------------------------------------
    # BUILD
    # ---------------------------------------

    def build(self):

        print("\nCREANDO EVENTOS DE AUDIO:\n")

        print("PISTAS DETECTADAS EN TEMPLATE:\n")

        for name in self.tracks:
            print("-", name)

        print("")

        for stem, track_type in self.matches:

            track = self.find_best_track(track_type)

            if track is None:

                print("No se encontró pista para:", track_type)
                continue

            event = self.clone_event()

            self.update_audio_paths(event, stem)

            self.insert_event(track, event)

            print("Evento creado:", stem)

        self.output_path.parent.mkdir(exist_ok=True)

        self.tree.write(
            str(self.output_path),
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8"
        )

        print("\nSesión generada en:")
        print(self.output_path)