from lxml import etree
from pathlib import Path
import uuid
import copy

from src.cubase_audio_resolver import CubaseAudioResolver


class SessionBuilder:

    def __init__(self, template_path, matches, output_path):

        self.template_path = Path(template_path)
        self.matches = matches
        self.output_path = Path(output_path)

        self.tree = etree.parse(str(self.template_path))
        self.root = self.tree.getroot()
        self.audio_resolver = CubaseAudioResolver(self.root)

        self.tracks = self.extract_tracks()
        self.template_event_source = self.get_template_event()

    def generate_id(self):
        return str(uuid.uuid4().int >> 64)

    # ---------------------------------------
    # DETECTAR PISTAS
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

    # ---------------------------------------
    # OBTENER EVENTO BASE
    # ---------------------------------------

    def get_template_event(self):

        event = self.root.find(".//obj[@class='MAudioEvent']")

        if event is None:
            raise Exception("Template no contiene MAudioEvent")

        return event

    def _get_global_fnpaths(self):

        # Solo FNPath globales en primer nivel: /tracklist2/obj[@class='FNPath']
        return self.root.xpath("./obj[@class='FNPath']")

    def _assign_event_path_id(self, event, path_id):

        for node in event.xpath(".//obj[@class='FNPath'][@ID]"):
            node.set("ID", path_id)

        for node in event.xpath(".//obj[@name='FPath'][@ID]"):
            node.set("ID", path_id)

    def _clear_all_template_audio_events(self):

        for events_list in self.root.xpath(".//list[@name='Events']"):
            for event in list(events_list):
                if event.tag == "obj" and event.get("class") == "MAudioEvent":
                    events_list.remove(event)

    # ---------------------------------------
    # CLONAR EVENTO
    # ---------------------------------------

    def clone_event(self, path_id):

        new_event = copy.deepcopy(self.template_event_source)

        # MAudioEvent siempre debe ser único
        new_event.set("ID", str(self.generate_id()))

        # Regenerar IDs internos de contenedores/eventos,
        # preservando nodos de path enlazados por ID.
        for obj in new_event.xpath(".//obj[@ID]"):

            if obj.get("class") == "FNPath":
                continue

            if obj.get("name") == "FPath":
                continue

            obj.set("ID", str(self.generate_id()))

        # Reusar ID de FNPath global existente del template.
        self._assign_event_path_id(new_event, path_id)

        return new_event

    # ---------------------------------------
    # ACTUALIZAR RUTAS DE AUDIO
    # ---------------------------------------

    def update_audio_paths(self, event, filename):
        self.audio_resolver.update_event_audio_references(event, filename)

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
        # track_node must be obj[@class='MListNode']
        events_list = track_node.find("./list[@name='Events']")

        if events_list is None:
            track_name = track_node.find("./string[@name='Name']")
            label = track_name.get("value") if track_name is not None else "unknown"
            raise Exception(f"No existe list[@name='Events'] en la pista: {label}")

        events_list.append(event)

    # ---------------------------------------
    # BUILD
    # ---------------------------------------

    def build(self):

        print("\nCREANDO EVENTOS DE AUDIO:\n")

        print("PISTAS DETECTADAS EN TEMPLATE:\n")

        for name in self.tracks:
            print("-", name)

        print("")

        # Limpiar eventos de audio originales del template para evitar referencias heredadas.
        self._clear_all_template_audio_events()

        available_fnpaths = self._get_global_fnpaths()

        used_fnpaths = []
        next_fnpath_idx = 0

        for stem, track_type in self.matches:

            track = self.find_best_track(track_type)

            if track is None:

                print("No se encontró pista para:", track_type)
                continue

            if next_fnpath_idx >= len(available_fnpaths):
                raise Exception(
                    f"Template tiene {len(available_fnpaths)} FNPath globales y no alcanza para los stems insertados."
                )

            global_fnpath = available_fnpaths[next_fnpath_idx]
            next_fnpath_idx += 1
            path_id = global_fnpath.get("ID")

            event = self.clone_event(path_id)

            self.update_audio_paths(event, stem)

            self.insert_event(track, event)
            used_fnpaths.append(global_fnpath)

            print("Evento creado:", stem)

        # Mantener sólo los FNPath globales usados por los stems insertados.
        for fnpath in available_fnpaths:
            if fnpath not in used_fnpaths:
                self.root.remove(fnpath)

        self.output_path.parent.mkdir(exist_ok=True)

        self.tree.write(
            str(self.output_path),
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8"
        )

        print("\nSesión generada en:")
        print(self.output_path)
