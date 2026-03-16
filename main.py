from pathlib import Path

from src.stem_reader import read_stems
from src.classifier import classify_stems
from src.matcher import match_stems
from src.file_manager import copy_and_rename_stems
from src.session_builder import SessionBuilder


def main():

    print("\n=== AUTOMATA ===\n")

    stems_folder = Path("stems")
    template_path = Path("templates/template_basic.xml")

    output_folder = Path("output")
    media_folder = output_folder / "Media"

    # 1 detectar stems
    stems = read_stems(stems_folder)

    print("STEMS ENCONTRADOS:\n")

    for s in stems:
        print("-", s)

    # 2 clasificar
    classified = classify_stems(stems)

    # 3 match con pistas
    matches = match_stems(classified)

    print("\nMATCHES:\n")

    for stem, track in matches:
        print(f"{stem} → {track}")

    # 4 copiar y renombrar archivos
    renamed = copy_and_rename_stems(
        stems_folder,
        media_folder,
        matches
    )

    # 5 generar XML usando nombres nuevos
    builder = SessionBuilder(
        template_path,
        renamed,
        output_folder / "session.xml"
    )

    builder.build()


if __name__ == "__main__":
    main()