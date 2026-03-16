class CubaseAudioResolver:

    def __init__(self, root):
        self.root = root

    def _set_fnpath(self, fnpath_node, filename):
        name_node = fnpath_node.find("./string[@name='Name']")
        if name_node is not None:
            name_node.set("value", filename)

        path_node = fnpath_node.find("./string[@name='Path']")
        if path_node is not None:
            path_node.set("value", "Media")

    def _update_description_and_clip_name(self, event, filename):
        base = filename.rsplit(".", 1)[0]

        desc = event.find("./string[@name='Description']")
        if desc is not None:
            desc.set("value", base)

        clip_name = event.find(".//obj[@class='PAudioClip']/string[@name='Name']")
        if clip_name is not None:
            clip_name.set("value", base)

    def _event_audio_path_ids(self, event):
        ids = set()

        for node in event.xpath(".//obj[@class='FNPath'][@ID]"):
            ids.add(node.get("ID"))

        for node in event.xpath(".//obj[@name='FPath'][@ID]"):
            ids.add(node.get("ID"))

        return {node_id for node_id in ids if node_id}

    def update_event_audio_references(self, event, filename):
        """
        Actualiza todas las referencias de audio de un MAudioEvent:
        - PAudioClip/FNPath
        - AudioCluster/Substreams/AudioFile/FPath (por ID compartido)
        """
        self._update_description_and_clip_name(event, filename)

        for fnpath in event.xpath(".//obj[@class='FNPath']"):
            self._set_fnpath(fnpath, filename)

        for path_id in self._event_audio_path_ids(event):
            for fnpath in self.root.xpath(f".//obj[@class='FNPath'][@ID='{path_id}']"):
                self._set_fnpath(fnpath, filename)

    def find_wav_references(self):
        return self.root.xpath(
            ".//obj[@class='FNPath']/string[@name='Name' and "
            "contains(translate(@value,'WAV','wav'),'.wav')]"
        )
