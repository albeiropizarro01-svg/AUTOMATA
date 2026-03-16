# src/classifier.py

KEYWORDS = {
    "kick": "KICK",
    "snare": "SNARE",
    "clap": "SNARE",
    "hat": "HIHAT",
    "hihat": "HIHAT",
    "808": "SUB-BASS",
    "bass": "BASS",
    "sub": "SUB-BASS",
    "pad": "AMBIENT",
    "piano": "KEYS",
    "lead": "LEAD",
    "vocal": "LEAD VOCAL",
    "vox": "LEAD VOCAL"
}


def classify_stems(stems):

    results = []

    for stem in stems:

        name = stem.lower()
        track_type = "UNKNOWN"

        for keyword, category in KEYWORDS.items():
            if keyword in name:
                track_type = category
                break

        results.append((stem, track_type))

    return results