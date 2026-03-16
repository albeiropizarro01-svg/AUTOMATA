from pathlib import Path
import shutil


def copy_and_rename_stems(stems_folder, media_folder, matches):

    media_folder.mkdir(parents=True, exist_ok=True)

    counters = {}

    renamed = []

    for stem, track in matches:

        track = track.upper()

        if track not in counters:
            counters[track] = 1
        else:
            counters[track] += 1

        if counters[track] == 1:
            new_name = f"{track}.wav"
        else:
            new_name = f"{track}_{counters[track]}.wav"

        src = Path(stems_folder) / stem
        dst = media_folder / new_name

        shutil.copy(src, dst)

        renamed.append((new_name, track))

    return renamed