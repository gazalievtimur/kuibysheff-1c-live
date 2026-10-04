"""Read the configuration name from a 1C XML dump."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


def configuration_xml(root: Path) -> Path | None:
    direct = root / "Configuration.xml"
    if direct.is_file():
        return direct
    matches = list(root.rglob("Configuration.xml"))
    return matches[0] if matches else None


def dump_root(path: Path) -> Path | None:
    xml_path = configuration_xml(path)
    if xml_path is None:
        return None
    return xml_path.parent


def configuration_name(root: Path) -> str:
    xml_path = configuration_xml(root)
    if xml_path is None:
        return root.name
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return root.name
    for node in tree.iter():
        if _local(node.tag) == "Properties":
            for child in list(node):
                if _local(child.tag) == "Name" and (child.text or "").strip():
                    return child.text.strip()
    return root.name


def _local(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag
