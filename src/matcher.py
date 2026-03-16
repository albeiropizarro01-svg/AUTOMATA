def match_stems(classified_stems):

    matches = []

    for stem, track_type in classified_stems:

        matches.append((stem, track_type))

    return matches