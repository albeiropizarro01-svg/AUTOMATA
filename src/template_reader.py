from pathlib import Path
from lxml import etree


def read_template(template_path):
    """
    Carga y valida un template de Cubase.

    Valida:
    - existencia del archivo
    - XML bien formado
    - presencia de al menos un MAudioEvent
    """

    path = Path(template_path)

    if not path.exists():
        raise FileNotFoundError(f"No se encontró el template: {template_path}")

    try:
        tree = etree.parse(str(path))
    except Exception as e:
        raise Exception(f"Error al parsear XML: {e}")

    root = tree.getroot()

    # validar evento base
    event = root.find(".//obj[@class='MAudioEvent']")
    if event is None:
        raise Exception("Template inválido: no contiene MAudioEvent")

    # validar tracks
    tracks = root.xpath(".//obj[@class='MListNode']")
    if not tracks:
        raise Exception("Template inválido: no contiene pistas (MListNode)")

    return tree