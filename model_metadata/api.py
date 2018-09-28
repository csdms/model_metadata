import os

from .errors import MetadataNotFoundError
from .model_setup import FileSystemLoader, OldFileSystemLoader
from .modelmetadata import ModelMetadata


def query(model, var):
    if os.path.isdir(model):
        path_to_mmd = model
    else:
        path_to_mmd = os.path.join(sys.prefix, "share", "csdms", model)
    if not os.path.isdir(path_to_mmd):
        raise MetadataNotFoundError(model)

    return ModelMetadata(path_to_mmd).get(var)


def stage(model, dest=".", old_style_templates=False):
    if os.path.isdir(model):
        mmd = model
    else:
        mmd = os.path.join(sys.prefix, "share", "csdms", model)

    if not os.path.isdir(mmd):
        raise MetadataNotFoundError(model)

    defaults = dict()
    meta = ModelMetadata(mmd)
    for param, item in meta.parameters.items():
        defaults[param] = item["value"]["default"]

    if old_style_templates:
        manifest = OldFileSystemLoader(mmd).stage_all(dest, **defaults)
    else:
        manifest = FileSystemLoader(mmd).stage_all(dest, **defaults)
    manifest = os.linesep.join(manifest)

    return manifest
