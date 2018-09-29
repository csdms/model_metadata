#! /usr/bin/env python
import os

from scripting.contexts import cd

from .errors import MetadataNotFoundError

_METADATA_FILES = {
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
}


def is_metadata_file(fname):
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


def find_metadata_files(datadir):
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
    try:
        with cd(datadir, create=False):
            found = [fname for fname in _METADATA_FILES if os.path.isfile(fname)]
    except OSError as err:
        if err.errno == 2:
            raise MetadataNotFoundError(datadir)
        else:
            raise

    return [os.path.join(datadir, fname) for fname in found]


def find_model_data_files(datadir):
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
        for dir in dirs:
            fnames.append(os.path.normpath(os.path.join(root, dir)) + os.sep)

        for fname in files:
            if not is_metadata_file(fname):
                fnames.append(os.path.normpath(os.path.join(root, fname)))

    return fnames
