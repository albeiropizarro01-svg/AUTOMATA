from lxml import etree
import uuid
import wave
from pathlib import Path


def read_wav_info(filepath):

    with wave.open(str(filepath), 'rb') as w:

        frames = w.getnframes()
        rate = w.getframerate()
        width = w.getsampwidth() * 8

    return frames, rate, width


class PoolBuilder:

    def __init__(self, root, media_path):
        self.root = root
        self.media_path = Path(media_path)

    def generate_id(self):
        return str(uuid.uuid4().int >> 64)

    def get_or_create_pool(self):

        pool = self.root.find(".//obj[@class='Pool']")

        if pool is None:
            pool = etree.SubElement(self.root, "obj")
            pool.set("class", "Pool")

        audio_list = pool.find("./list[@name='AudioFiles']")

        if audio_list is None:
            audio_list = etree.SubElement(pool, "list")
            audio_list.set("name", "AudioFiles")
            audio_list.set("type", "obj")

        return audio_list

    # 🔥 CAMBIO: ahora recibe path_id también
    def add_audio_file(self, filename, audio_id, path_id):

        audio_list = self.get_or_create_pool()

        # ✅ evitar duplicados por path_id
        existing = audio_list.xpath(f"./obj[obj[@name='FPath'][@ID='{path_id}']]")
        if existing:
            return existing[0]

        audio_file = etree.SubElement(audio_list, "obj")
        audio_file.set("class", "AudioFile")

        # ID del AudioFile (POOL)
        audio_file.set("ID", audio_id)

        # 🔥 conexión REAL con FNPath usando path_id
        fpath = etree.SubElement(audio_file, "obj")
        fpath.set("name", "FPath")
        fpath.set("ID", path_id)

        name = etree.SubElement(audio_file, "string")
        name.set("name", "Name")
        name.set("value", filename)

        path = etree.SubElement(audio_file, "string")
        path.set("name", "Path")
        path.set("value", "Media")

        filepath = self.media_path / filename

        frames, rate, sample_size = read_wav_info(filepath)

        frame_node = etree.SubElement(audio_file, "int")
        frame_node.set("name", "FrameCount")
        frame_node.set("value", str(frames))

        rate_node = etree.SubElement(audio_file, "float")
        rate_node.set("name", "Rate")
        rate_node.set("value", str(rate))

        size_node = etree.SubElement(audio_file, "int")
        size_node.set("name", "Sample Size")
        size_node.set("value", str(sample_size))

        return audio_file