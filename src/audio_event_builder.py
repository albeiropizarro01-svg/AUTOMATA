from lxml import etree as ET
import uuid


def generate_id():
    return str(uuid.uuid4().int >> 64)


class AudioEventBuilder:

    def _find_template_event(self, root):
        """
        Busca un MAudioEvent existente para usarlo como plantilla
        """
        return root.find(".//obj[@class='MAudioEvent']")


    def _find_track_events_list(self, root, track_name):

        target = track_name.strip().lower()

        for node in root.findall(".//obj[@class='MListNode']"):

            name_node = node.find("./string[@name='Name']")

            if name_node is None:
                continue

            name = name_node.attrib.get("value", "").lower()

            if name == target:

                events = node.find("./list[@name='Events']")

                if events is not None:
                    return events

        return None


    def _replace_audio_path(self, event, filename):

        fnpath = event.find(".//obj[@class='FNPath']")

        if fnpath is None:
            return

        name_node = fnpath.find("./string[@name='Name']")

        if name_node is not None:
            name_node.attrib["value"] = filename

        path_node = fnpath.find("./string[@name='Path']")

        if path_node is not None:
            path_node.attrib["value"] = "Media"


    def _update_clip_names(self, event, filename):

        base = filename.replace(".wav", "")

        # description del evento
        desc = event.find("./string[@name='Description']")

        if desc is not None:
            desc.attrib["value"] = base

        # nombre del clip
        clip = event.find(".//obj[@class='PAudioClip']")

        if clip is not None:

            name_node = clip.find("./string[@name='Name']")

            if name_node is not None:
                name_node.attrib["value"] = base


    def add_audio_event_to_track(self, root, track_name, filename):

        template_event = self._find_template_event(root)

        if template_event is None:
            print("No se encontró evento plantilla en el template.")
            return False

        # clonar evento
        new_event = ET.fromstring(ET.tostring(template_event))

        # nuevo ID
        new_event.attrib["ID"] = generate_id()

        # cambiar path del audio
        self._replace_audio_path(new_event, filename)

        # actualizar nombres visibles
        self._update_clip_names(new_event, filename)

        # encontrar pista
        events_list = self._find_track_events_list(root, track_name)

        if events_list is None:
            print(f"No se encontró pista: {track_name}")
            return False

        events_list.append(new_event)

        return True