from lxml import etree


class CubaseAudioResolver:

    def __init__(self, root):

        self.root = root

    # ---------------------------------------
    # encontrar todas las referencias a audio
    # ---------------------------------------

    def find_audio_nodes(self):

        nodes = []

        for node in self.root.xpath(".//string"):

            value = node.get("value")

            if value is None:
                continue

            if value.lower().endswith(".wav"):
                nodes.append(node)

        return nodes

    # ---------------------------------------
    # actualizar nombres de archivo
    # ---------------------------------------

    def replace_audio_filename(self, old_name, new_name):

        for node in self.find_audio_nodes():

            value = node.get("value")

            if value.lower() == old_name.lower():
                node.set("value", new_name)

    # ---------------------------------------
    # actualizar rutas
    # ---------------------------------------

    def force_media_folder(self):

        for node in self.root.xpath(".//string[@name='Path']"):

            node.set("value", "Media")

    # ---------------------------------------
    # debug para ver qué está usando Cubase
    # ---------------------------------------

    def print_audio_references(self):

        print("\nREFERENCIAS DE AUDIO DETECTADAS:\n")

        for node in self.find_audio_nodes():

            print(node.get("value"))