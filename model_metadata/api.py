import os

from .model_setup import FileSystemLoader, OldFileSystemLoader
from .modelmetadata import ModelMetadata
from .scripting import cp, ln_s


def find(model):
    """Attempt to find a model's metadata.

    Parameters
    ----------
    model : path, str or object
        The model is interpreted either as a path to a folder that
        contains metadata, the name of a model component, or a
        model object.

    Returns
    -------
    Path
        Path to the folder that contains the model's metadata.

    Raises
    ------
    MetadataNotFoundError
        If a metadata folder cannot be found.
    """
    return ModelMetadata.find(model)


def query(model, var):
    """Query metadata for a particular variable (or section).

    Parameters
    ----------
    model : path, str or object
        The model is interpreted either as a path to a folder that
        contains metadata, the name of a model component, or a
        model object.
    var : str
        Name of a variable to query. The should be given in "dotted notation".
        That is, to query the variable *url* in the *info* section, use
        *"info.url"*. To get the entire *info* section just use *"info"*.

    Returns
    -------
    object
        The requested variable.
    """
    path_to_metadata = ModelMetadata.find(model)
    return ModelMetadata(path_to_metadata).get(var)


def stage(model, dest=".", old_style_templates=False):
    """Stage a model by setting up its input files.

    Parameters
    ----------
    model : path, str or object
        The model is interpreted either as a path to a folder that
        contains metadata, the name of a model component, or a
        model object.
    dest : str
        Path to a folder within which to stage the model.
    """
    defaults = dict()
    mmd = ModelMetadata.find(model)
    meta = ModelMetadata(mmd)
    for param, item in meta.parameters.items():
        defaults[param] = item["value"]["default"]

    if old_style_templates:
        manifest = OldFileSystemLoader(mmd).stage_all(dest, **defaults)
    else:
        manifest = FileSystemLoader(mmd).stage_all(dest, **defaults)

    return manifest


def install(path, dest, develop=False, silent=True, dry_run=False, clobber=False):
    from jinja2 import Environment, FileSystemLoader

    templates = Environment(loader=FileSystemLoader(path)).list_templates()
    for fname in templates:
        if develop:
            install = ln_s
        else:
            install = cp
        install(
            os.path.join(path, fname),
            os.path.join(dest, fname),
            silent=silent,
            dry_run=dry_run,
            create_dirs=True,
            clobber=clobber,
        )
