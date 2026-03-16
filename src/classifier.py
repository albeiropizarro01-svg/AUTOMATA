KEYWORDS = {

    "kick": "KICK",
    "808": "BASS",
    "bass": "BASS",
    "snare": "SNARE",
    "clap": "SNARE",
    "hat": "HIHAT",
    "vocal": "VOCAL",
    "lead": "LEAD",
    "pad": "AMBIENT",
    "piano": "KEYS"
}


def classify_stems(stems):

    classified = []

    for stem in stems:

        stem_lower = stem.lower()

        track_type = None

        for keyword in KEYWORDS:

            if keyword in stem_lower:
                track_type = KEYWORDS[keyword]
                break

        if track_type is None:
            track_type = "OTHER"

        classified.append((stem, track_type))

    return classified