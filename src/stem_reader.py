from pathlib import Path


def read_stems(stems_folder):

    stems = []

    stems_folder = Path(stems_folder)

    for file in stems_folder.iterdir():

        if file.suffix.lower() == ".wav":
            stems.append(file.name)

    return stems