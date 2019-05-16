import os
import sys

from scripting import cp, ln_s

from .errors import MetadataNotFoundError
from .model_setup import FileSystemLoader, OldFileSystemLoader
from .modelmetadata import ModelMetadata


def query(model, var):
    try:
        if os.path.isdir(model.METADATA):
            model = model.METADATA
    except AttributeError:
        pass

    if os.path.isdir(model):
        path_to_mmd = model
    else:
        path_to_mmd = os.path.join(sys.prefix, "share", "csdms", model)
    if not os.path.isdir(path_to_mmd):
        raise MetadataNotFoundError(path_to_mmd)

    return ModelMetadata(path_to_mmd).get(var)


def stage(model, dest=".", old_style_templates=False):
    try:
        if os.path.isdir(model.METADATA):
            model = model.METADATA
    except AttributeError:
        pass

    if os.path.isdir(model):
        mmd = model
    else:
        mmd = os.path.join(sys.prefix, "share", "csdms", model)

    if not os.path.isdir(mmd):
        raise MetadataNotFoundError(mmd)

    defaults = dict()
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
