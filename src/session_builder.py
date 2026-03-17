from lxml import etree
from pathlib import Path
import uuid
import copy
import wave

from src.cubase_audio_resolver import CubaseAudioResolver


def generate_hex_uuid():
    return uuid.uuid4().hex.upper()


def get_wav_info(path):

    with wave.open(str(path), "rb") as w:
        frames = w.getnframes()
        rate = w.getframerate()
        channels = w.getnchannels()
        sampwidth = w.getsampwidth()

    return frames, rate, channels, sampwidth


class SessionBuilder:

    def __init__(self, template_path, matches, output_path):

        self.template_path = Path(template_path)
        self.matches = matches
        self.output_path = Path(output_path)

        self.tree = etree.parse(str(self.template_path))
        self.root = self.tree.getroot()

        self.media_folder = self.output_path.parent / "Media"

        self.audio_resolver = CubaseAudioResolver(self.root)

        self.tracks = self.extract_tracks()
        self.template_event_source = self.get_template_event()

    def generate_id(self):
        return str(uuid.uuid4().int >> 64)

    # ---------------------------------------
    # TRACKS
    # ---------------------------------------

    def extract_tracks(self):

        tracks = {}

        for node in self.root.xpath(".//obj[@class='MListNode']"):

            name_node = node.find("./string[@name='Name']")

            if name_node is None:
                continue

            name = name_node.get("value")

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

    def get_template_event(self):

        event = self.root.find(".//obj[@class='MAudioEvent']")

        if event is None:
            raise Exception("Template no contiene MAudioEvent")

        return event

    # ---------------------------------------
    # FNPath
    # ---------------------------------------

    def create_fnpath(self, filename):

        fnpath = etree.SubElement(self.root, "obj")
        fnpath.set("class", "FNPath")
        fnpath.set("ID", self.generate_id())

        # nombre del archivo
        name = etree.SubElement(fnpath, "string")
        name.set("name", "Name")
        name.set("value", filename)

        # ruta absoluta REAL
        abs_path = str(self.media_folder.resolve())

        path = etree.SubElement(fnpath, "string")
        path.set("name", "Path")
        path.set("value", abs_path)

        # tipo de ruta (2 = absoluta)
        path_type = etree.SubElement(fnpath, "int")
        path_type.set("name", "PathType")
        path_type.set("value", "2")

        return fnpath

    def clear_fnpaths(self):
        for fn in self.root.xpath(".//obj[@class='FNPath']"):
            parent = fn.getparent()
            if parent is not None:
                parent.remove(fn)

    def assign_event_path_id(self, event, path_id):

        for node in event.xpath(".//obj[@class='FNPath'][@ID]"):
            node.set("ID", path_id)

        for node in event.xpath(".//obj[@name='FPath'][@ID]"):
            node.set("ID", path_id)

    # ---------------------------------------
    # EVENTOS
    # ---------------------------------------

    def clear_template_events(self):

        for events_list in self.root.xpath(".//list[@name='Events']"):
            for event in list(events_list):
                if event.tag == "obj" and event.get("class") == "MAudioEvent":
                    events_list.remove(event)

    def clone_event(self, path_id):

        new_event = copy.deepcopy(self.template_event_source)

        new_event.set("ID", self.generate_id())

        for obj in new_event.xpath(".//obj[@ID]"):

            if obj.get("class") == "FNPath":
                continue

            if obj.get("name") == "FPath":
                continue

            if obj.get("name") == "Stream":
                obj.attrib.pop("ID", None)
                continue

            obj.set("ID", self.generate_id())

        self.assign_event_path_id(new_event, path_id)

        return new_event

    # ---------------------------------------
    # TRACK MATCH
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

    def insert_event(self, track_node, event):

        events_list = track_node.find("./list[@name='Events']")

        if events_list is None:
            raise Exception("Track sin lista de eventos")

        events_list.append(event)

    # ---------------------------------------
    # BUILD
    # ---------------------------------------

    def build(self):

        print("\nCREANDO EVENTOS DE AUDIO:\n")

        self.clear_template_events()
        self.clear_fnpaths()
        abs_media_path = str(self.media_folder.resolve())

        for stem, track_type in self.matches:

            track = self.find_best_track(track_type)

            if track is None:
                print("No se encontró pista para:", track_type)
                continue

            fnpath = self.create_fnpath(stem)
            path_id = fnpath.get("ID")

            event = self.clone_event(path_id)

            audio_file = event.find(".//obj[@class='AudioFile']")

            audio_id = self.generate_id()
            audio_file.set("ID", audio_id)

            stream = audio_file.find("./obj[@name='Stream']")
            if stream is not None:
                stream.set("ID", audio_id)

            fpath = audio_file.find("./obj[@name='FPath']")
            if fpath is not None:
                fpath.set("ID", path_id)

            self.audio_resolver.update_event_audio_references(event, stem)

            audio_path = self.media_folder / stem
            frames, rate, channels, sampwidth = get_wav_info(audio_path)

            frame_node = audio_file.find("./int[@name='FrameCount']")
            rate_node = audio_file.find("./float[@name='Rate']")

            if frame_node is not None:
                frame_node.set("value", str(frames))

            if rate_node is not None:
                rate_node.set("value", str(rate))

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
        
       