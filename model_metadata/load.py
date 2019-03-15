import os

import yaml


def load_yaml_file(file_like):
    try:
        contents = file_like.read()
    except AttributeError:
        if os.path.isfile(file_like):
            with open(file_like, "r") as fp:
                contents = fp.read()
        else:
            contents = None

    if contents:
        return _merge_documents(yaml.safe_load_all(contents))
    else:
        return None


def load_meta_section(path, section):
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
    meta_path = os.path.join(path, "meta.yaml")
    meta = load_yaml_file(meta_path) or {}

    try:
        meta_section = meta[section]
    except KeyError:
        section_path = os.path.join(path, "{section}.yaml".format(section=section))
        meta_section = load_yaml_file(section_path) or {}

    return meta_section


def _merge_documents(documents):
    merged = {}
    for document in documents:
        merged.update(document)
    return merged
