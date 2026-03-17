import re

# prioridad de clasificación (de mayor a menor)
CLASS_PRIORITY = [
    ("KICK", ["kick"]),
    ("SNARE", ["snare", "clap"]),
    ("HIHAT", ["hat", "hihat"]),
    ("BASS", ["bass", "808"]),
    ("KEYS", ["piano", "keys"]),
    ("AMBIENT", ["pad", "ambient"]),
    ("VOCAL", ["vocal", "vox"]),
    ("LEAD", ["lead"])
]


def tokenize(filename):
    """
    Convierte:
    'Kick_808-Soft.wav' → ['kick', '808', 'soft']
    """
    name = filename.lower().replace(".wav", "")

    tokens = re.split(r"[_\-\s]+", name)

    return [t for t in tokens if t]


def classify_stem(stem):

    tokens = tokenize(stem)

    for track_type, keywords in CLASS_PRIORITY:

        for keyword in keywords:

            if keyword in tokens:
                return track_type

    return "OTHER"


def classify_stems(stems):

    classified = []

    for stem in stems:

        track_type = classify_stem(stem)

        classified.append((stem, track_type))

    return classified