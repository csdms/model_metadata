from __future__ import annotations

import io
import os
from collections.abc import Iterable
from typing import Any

import yaml


def _load_yaml_file(file_like: io.TextIOBase | str) -> dict[str, Any]:
    if not isinstance(file_like, str):
        contents = file_like.read()
    elif os.path.isfile(file_like):
        with open(file_like) as fp:
            contents = fp.read()
    else:
        return {}
    return _merge_documents(yaml.safe_load_all(contents))


def load_meta_section(path: str, section: str) -> dict[str, Any]:
    """Load a section from a model metadata file.

    Parameters
    ----------
    path : str
        Path to the folder containing model metadata.
    section : str
        The name of the section to load.

    Returns
    -------
    dict
        The metadata from the section.
    """
    meta = _load_yaml_file(os.path.join(path, "meta.yaml"))

    try:
        meta_section = meta[section]
    except KeyError:
        meta_section = _load_yaml_file(os.path.join(path, f"{section}.yaml"))

    return meta_section


def _merge_documents(documents: Iterable[dict[str, Any]]) -> dict[str, Any]:
    merged = {}
    for document in documents:
        merged.update(document)
    return merged
