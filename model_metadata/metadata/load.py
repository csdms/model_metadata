#! /usr/bin/env python
import os

import yaml


def model_data_dir(name, datarootdir=None):
    """Get a model's data dir.

    Parameters
    ----------
    name : str
        The name of the model.

    Returns
    -------
    str
        The absolute path to the data directory for the model.
    """
    datarootdir = datarootdir or os.path.join(sys.prefix, 'share')
    # datarootdir = query_config_var('datarootdir')
    return os.path.join(datarootdir, 'csdms', name)


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
    meta_path = os.path.join(path, 'meta.yaml')
    meta = load_yaml_file(meta_path) or {}

    try:
        meta_section = meta[section]
    except KeyError:
        section_path = os.path.join(path,
                                    '{section}.yaml'.format(section=section))
        meta_section = load_yaml_file(section_path) or {}

    return meta_section


def merge_documents(documents):
    merged = {}
    for document in documents:
        merged.update(document)
    return merged


def load_yaml_file(file_like):
    try:
        contents = file_like.read()
    except AttributeError:
        if os.path.isfile(file_like):
            with open(file_like, 'r') as fp:
                contents = fp.read()
        else:
            contents = None

    if contents:
        return merge_documents(yaml.load_all(contents))
        # return yaml.load(contents)
    else:
        return None


def load_metadata(name):
    """Load all metadata for a model.

    Parameters
    ----------
    name : str
        Name of model.

    Returns
    -------
    dict
        A dictionary of the model metadata. There are two keys, 'defaults'
        for the default parameters and 'info' for model metadata.
    """
    meta = dict()

    datadir = model_data_dir(name)
    meta['defaults'] = load_default_parameters(datadir)
    meta['info'] = load_info_section(datadir)
    meta['run'] = load_run_section(datadir)
    meta['names'] = load_names_section(datadir)

    parameters = dict()
    for name, param in meta['defaults'].items():
        parameters[name] = param.value, param.units
    meta['parameters'] = parameters

    return meta
