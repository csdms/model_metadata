#! /usr/bin/env python
from __future__ import annotations

import os

from model_metadata.errors import MetadataNotFoundError

_METADATA_FILES = frozenset(
    (
        "api.yaml",
        "api.yml",
        "parameters.yaml",
        "parameters.yml",
        "info.yaml",
        "info.yml",
        "wmt.yaml",
        "wmt.yml",
        "run.yaml",
        "run.yml",
    )
)


def is_metadata_file(fname: str) -> bool:
    """Check if a file is a model metadat file.

    Parameters
    ----------
    fname : str
        Name of file to check.

    Returns
    -------
    bool
        `True` if the file is a model metadata file. Otherwise, `False`.
    """
    return os.path.basename(fname) in _METADATA_FILES


def find_metadata_files(datadir: str) -> tuple[str, ...]:
    """Find all model metadata files.

    Parameters
    ----------
    datadir : str
        Path to folder to search under.

    Returns
    -------
    list of str
        Paths to all metadata files.
    """
    found = tuple(
        path_to_file
        for fname in _METADATA_FILES
        if os.path.isfile(path_to_file := os.path.join(datadir, fname))
    )
    if not found:
        raise MetadataNotFoundError(datadir)
    else:
        return found


def find_model_data_files(datadir: str) -> tuple[str, ...]:
    """Look for model data files.

    Parameters
    ----------
    datadir : str
        Path the the model's data directory.

    Returns
    -------
    list of str
        List of the data files relative to their data directory.
    """
    fnames = []
    for root, dirs, files in os.walk(datadir):
        for dir_ in dirs:
            fnames.append(os.path.normpath(os.path.join(root, dir_)) + os.sep)

        for fname in files:
            if not is_metadata_file(fname):
                fnames.append(os.path.normpath(os.path.join(root, fname)))

    return tuple(fnames)
