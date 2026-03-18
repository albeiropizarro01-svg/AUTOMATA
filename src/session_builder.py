from lxml import etree
from pathlib import Path
import uuid
import copy
import wave


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

        self.tracks = self.extract_tracks()
        self.template_event_source = self.get_template_event()

    def generate_id(self):
        return str(uuid.uuid4().int >> 64)

    # ----------------------------------------
    # TRACKS
    # ----------------------------------------

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
                "stereo out",
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

    # ----------------------------------------
    # FNPath helpers
    # ----------------------------------------

    def _set_or_create_scalar(self, parent, tag, name, value):
        node = parent.find(f"./{tag}[@name='{name}']")
        if node is None:
            node = etree.SubElement(parent, tag)
            node.set("name", name)
        node.set("value", value)
        return node

    def _set_fnpath_values(self, fnpath_node, filename, abs_media_path):
        self._set_or_create_scalar(fnpath_node, "string", "Name", filename)
        self._set_or_create_scalar(fnpath_node, "string", "Path", abs_media_path)
        self._set_or_create_scalar(fnpath_node, "int", "PathType", "2")

    def _create_global_fnpath(self, filename, abs_media_path, forced_id):
        fnpath = etree.SubElement(self.root, "obj")
        fnpath.set("class", "FNPath")
        fnpath.set("ID", forced_id)

        self._set_fnpath_values(fnpath, filename, abs_media_path)
        return fnpath

    def clear_global_fnpaths(self):
        for fn in self.root.xpath(".//obj[@class='FNPath']"):
            self.root.remove(fn)

    def clear_pool(self):
        for pool in self.root.xpath(".//obj[@class='Pool']"):
            parent = pool.getparent()
            if parent is not None:
                parent.remove(pool)

    # ----------------------------------------
    # EVENTOS
    # ----------------------------------------

    def clear_template_events(self):

        for events_list in self.root.xpath(".//list[@name='Events']"):
            for event in list(events_list):
                if event.tag == "obj" and event.get("class") == "MAudioEvent":
                    events_list.remove(event)

    def clone_event(self):

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

        return new_event

    def rebuild_event_media_graph(self, event, original_filename, abs_media_path):

        base = Path(original_filename).stem

        desc = event.find("./string[@name='Description']")
        if desc is not None:
            desc.set("value", base)

        clip_name = event.find(".//obj[@class='PAudioClip']/string[@name='Name']")
        if clip_name is not None:
            clip_name.set("value", base)

        clip_fnpath = event.find(".//obj[@class='PAudioClip']/obj[@class='FNPath']")
        if clip_fnpath is None:
            raise Exception("Evento inválido: falta PAudioClip/FNPath")

        audio_file = event.find(".//obj[@class='PAudioClip']//obj[@class='AudioFile']")
        if audio_file is None:
            raise Exception("Evento inválido: falta AudioFile")

        for stale in event.xpath(".//obj[@class='FNPath']"):
            if stale is clip_fnpath:
                continue
            parent = stale.getparent()
            if parent is not None:
                parent.remove(stale)

        audio_id = self.generate_id()
        clip_path_id = self.generate_id()
        archive_path_id = self.generate_id()
        orig_path_id = self.generate_id()

        clip_fnpath.set("ID", clip_path_id)
        self._set_fnpath_values(clip_fnpath, original_filename, abs_media_path)

        orig_ref = clip_fnpath.find("./obj[@name='OrigPath']")
        if orig_ref is None:
            orig_ref = etree.SubElement(clip_fnpath, "obj")
            orig_ref.set("name", "OrigPath")
        orig_ref.set("ID", orig_path_id)

        audio_file.set("ID", audio_id)

        stream = audio_file.find("./obj[@name='Stream']")
        if stream is None:
            stream = etree.SubElement(audio_file, "obj")
            stream.set("name", "Stream")
        stream.set("ID", audio_id)

        fpath = audio_file.find("./obj[@name='FPath']")
        if fpath is None:
            fpath = etree.SubElement(audio_file, "obj")
            fpath.set("name", "FPath")
        fpath.set("ID", clip_path_id)

        archive_path = audio_file.find("./obj[@name='archivePath']")
        if archive_path is None:
            archive_path = etree.SubElement(audio_file, "obj")
            archive_path.set("name", "archivePath")
        archive_path.set("ID", archive_path_id)

        self._create_global_fnpath(original_filename, abs_media_path, archive_path_id)
        self._create_global_fnpath(original_filename, abs_media_path, orig_path_id)

    # ----------------------------------------
    # TRACK MATCH
    # ----------------------------------------

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

        events_list = track_node.find(".//list[@name='Events']")

        if events_list is None:
            raise Exception("Track sin lista de eventos")

        events_list.append(event)

    # ----------------------------------------
    # BUILD
    # ----------------------------------------

    def build(self):

        print("\nCREANDO EVENTOS DE AUDIO:\n")

        self.clear_template_events()
        self.clear_global_fnpaths()
        self.clear_pool()

        abs_media_path = str(self.media_folder.resolve())

        for original_filename, track_type in self.matches:

            track = self.find_best_track(track_type)

            if track is None:
                print("No se encontró pista para:", track_type)
                continue

            event = self.clone_event()
            self.rebuild_event_media_graph(event, original_filename, abs_media_path)

            audio_file = event.find(".//obj[@class='AudioFile']")

            audio_path = self.media_folder / original_filename
            frames, rate, channels, sampwidth = get_wav_info(audio_path)

            frame_node = audio_file.find("./int[@name='FrameCount']")
            rate_node = audio_file.find("./float[@name='Rate']")

            if frame_node is not None:
                frame_node.set("value", str(frames))

            if rate_node is not None:
                rate_node.set("value", str(rate))

            self.insert_event(track, event)

            print("Evento creado:", original_filename)

        self.output_path.parent.mkdir(exist_ok=True)

        self.tree.write(
            str(self.output_path),
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8"
        )
