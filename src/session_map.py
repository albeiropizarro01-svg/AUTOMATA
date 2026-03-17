from src.classifier import classify_stems


def build_session_map(stems):
    """
    Genera un preview del mapping:
    stem → tipo de pista (no template real)

    Esto es SOLO informativo.
    El mapping real ocurre en SessionBuilder.
    """

    classified = classify_stems(stems)

    session_map = {}

    for stem, track_type in classified:

        if track_type not in session_map:
            session_map[track_type] = []

        session_map[track_type].append(stem)

    return session_map


def print_session_map(session_map):
    """
    Visualización limpia del mapping
    """

    print("\nSESSION MAP\n")

    for track_type, stems in session_map.items():

        print(track_type)

        for stem in stems:
            print("   ", stem)