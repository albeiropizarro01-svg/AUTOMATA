from pathlib import Path


VALID_EXTENSIONS = {".wav"}


def read_stems(stems_folder):
    """
    Lee y filtra archivos de audio válidos.

    Retorna:
    list[str] → nombres de archivos
    """

    stems_folder = Path(stems_folder)

    if not stems_folder.exists():
        raise FileNotFoundError(f"No existe la carpeta de stems: {stems_folder}")

    if not stems_folder.is_dir():
        raise Exception(f"La ruta no es una carpeta válida: {stems_folder}")

    stems = []

    for file in stems_folder.iterdir():

        # ignorar archivos ocultos
        if file.name.startswith("."):
            continue

        # validar extensión
        if file.suffix.lower() not in VALID_EXTENSIONS:
            continue

        stems.append(file.name)

    # orden determinista
    stems.sort()

    return stems