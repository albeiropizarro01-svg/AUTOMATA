class CubaseAudioResolver:

    def __init__(self, root):
        self.root = root

    # ---------------------------------------
    # NORMALIZACIÓN
    # ---------------------------------------

    def _normalize_filename(self, filename):
        filename = filename.strip()

        if not filename.lower().endswith(".wav"):
            filename += ".wav"

        return filename

    def _basename(self, filename):
        return filename.replace(".wav", "")

    # ---------------------------------------
    # FNPath
    # ---------------------------------------

    def _set_fnpath(self, fnpath_node, filename):

        name_node = fnpath_node.find("./string[@name='Name']")
        if name_node is not None:
            name_node.set("value", filename)

        path_node = fnpath_node.find("./string[@name='Path']")
        if path_node is not None:
            path_node.set("value", "Media")

    # ---------------------------------------
    # EVENTO
    # ---------------------------------------

    def _update_event_labels(self, event, filename):

        base = self._basename(filename)

        # Description
        desc = event.find("./string[@name='Description']")
        if desc is not None:
            desc.set("value", base)

        # Clip name
        clip_name = event.find(".//obj[@class='PAudioClip']/string[@name='Name']")
        if clip_name is not None:
            clip_name.set("value", base)

    # ---------------------------------------
    # IDS RELACIONADOS
    # ---------------------------------------

    def _collect_path_ids(self, event):

        ids = set()

        # SOLO FNPath del evento principal
        for node in event.xpath(".//obj[@class='FNPath'][@ID]"):
            ids.add(node.get("ID"))

        return {i for i in ids if i}

    # ---------------------------------------
    # ACTUALIZACIÓN PRINCIPAL
    # ---------------------------------------

    def update_event_audio_references(self, event, filename):
        """
        Actualiza TODAS las referencias de audio:
        - nombres visibles
        - FNPath locales
        - FNPath globales por ID
        """

        filename = self._normalize_filename(filename)

        # actualizar labels visibles
        self._update_event_labels(event, filename)

        # actualizar FNPath del clip
        for fnpath in event.xpath(".//obj[@class='PAudioClip']/obj[@class='FNPath']"):
            self._set_fnpath(fnpath, filename)

        # actualizar todos los FNPath relacionados por ID
        path_ids = self._collect_path_ids(event)

        for path_id in path_ids:

            for fnpath in self.root.xpath(f".//obj[@class='FNPath'][@ID='{path_id}']"):
                self._set_fnpath(fnpath, filename)

    # ---------------------------------------
    # DEBUG
    # ---------------------------------------

    def find_all_wav_references(self):
        """
        Útil para debugging: lista todos los FNPath con .wav
        """
        return self.root.xpath(
            ".//obj[@class='FNPath']/string[@name='Name' and "
            "contains(translate(@value,'WAV','wav'),'.wav')]"
        )