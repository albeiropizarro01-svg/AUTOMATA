from lxml import etree as ET
import uuid

def generate_id():
"""Generate Cubase-compatible numeric ID"""
return str(uuid.uuid4().int >> 64)

class AudioEventBuilder:

```
def create_audio_file(self, filename):
    audio_file_id = generate_id()

    audio_file = ET.Element("obj", {
        "class": "AudioFile",
        "ID": audio_file_id
    })

    file_member = ET.SubElement(audio_file, "member", name="FilePath")

    fnpath = ET.SubElement(file_member, "obj", {
        "class": "FNPath"
    })

    ET.SubElement(fnpath, "string", name="Path", value="Media")
    ET.SubElement(fnpath, "string", name="Name", value=filename)

    return audio_file, audio_file_id


def create_audio_clip(self, audio_file_id):
    clip_id = generate_id()

    clip = ET.Element("obj", {
        "class": "PAudioClip",
        "ID": clip_id
    })

    member = ET.SubElement(clip, "member", name="AudioFile")

    ET.SubElement(member, "obj", {
        "ref": audio_file_id
    })

    return clip, clip_id


def create_audio_event(self, clip_id):
    event_id = generate_id()

    event = ET.Element("obj", {
        "class": "MAudioTrackEvent",
        "ID": event_id
    })

    start_member = ET.SubElement(event, "member", name="Start")
    start_member.text = "0"

    # Cubase necesita una longitud mayor que 0
    length_member = ET.SubElement(event, "member", name="Length")
    length_member.text = "441000"

    offset_member = ET.SubElement(event, "member", name="Offset")
    offset_member.text = "0"

    clip_member = ET.SubElement(event, "member", name="AudioClip")

    ET.SubElement(clip_member, "obj", {
        "ref": clip_id
    })

    return event
```
