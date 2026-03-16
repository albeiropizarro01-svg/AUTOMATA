from lxml import etree
import uuid


class PoolBuilder:

    def __init__(self, root):
        self.root = root

    def generate_id(self):
        return str(uuid.uuid4())

    def add_audio_file(self, filename):

        pool = self.root.find(".//obj[@class='Pool']")

        audio_file = etree.SubElement(pool, "obj")
        audio_file.set("class", "AudioFile")
        audio_file.set("ID", self.generate_id())

        name = etree.SubElement(audio_file, "string")
        name.set("name", "Name")
        name.set("value", filename)

        path = etree.SubElement(audio_file, "string")
        path.set("name", "Path")
        path.set("value", "Media")

        return audio_file