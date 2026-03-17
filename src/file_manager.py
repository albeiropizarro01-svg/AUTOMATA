from pathlib import Path
import shutil


def copy_stems(stems_folder, media_folder, matches):

    media_folder.mkdir(parents=True, exist_ok=True)

    copied = []

    for stem, track in matches:

        src = Path(stems_folder) / stem
        dst = media_folder / stem  # ← mantener nombre original

        shutil.copy(src, dst)

        copied.append((stem, track))  # ← NO cambiar nombre

    return copied