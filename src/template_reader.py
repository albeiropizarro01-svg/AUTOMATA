from pathlib import Path
from lxml import etree as ET


def read_template(template_path):

    path = Path(template_path)

    if not path.exists():
        raise FileNotFoundError(f"No se encontró el template: {template_path}")

    tree = ET.parse(str(path))

    return tree