from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from model_metadata.errors import UnknownKeyError
from model_metadata.model_setup import FileSystemLoader
from model_metadata.model_setup import OldFileSystemLoader
from model_metadata.modelmetadata import ModelMetadata


def find(model: str | type) -> str:
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


def query(model: str, var: str) -> ModelMetadata:
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


def stage(
    model: str,
    dest: str = ".",
    old_style_templates: bool = False,
    parameters: dict[str, Any] | None = None,
) -> tuple[str, ...]:
    """Stage a model by setting up its input files.

    Parameters
    ----------
    model : path, str or object
        The model is interpreted either as a path to a folder that
        contains metadata, the name of a model component, or a
        model object.
    dest : str, optional
        Path to a folder within which to stage the model.
    parameters : dict[str, Any], optional
        A dictionary of parameters that overrides the default
        values.
    """
    parameters = {} if parameters is None else parameters

    defaults = {}
    mmd = ModelMetadata.find(model)
    meta = ModelMetadata(mmd)
    for param, item in meta.parameters.items():
        defaults[param] = item["value"]["default"]

    try:
        _check_for_unknown_keys(defaults.keys(), parameters.keys())
    except UnknownKeyError as e:
        e.add_note(
            f"valid parameter{'s' if len(defaults) > 1 else ''}:"
            f" {', '.join(sorted(repr(k) for k in defaults))}"
        )
        raise

    defaults = {**defaults, **parameters}

    if old_style_templates:
        manifest = OldFileSystemLoader(mmd).stage_all(dest, **defaults)
    else:
        manifest = FileSystemLoader(mmd).stage_all(dest, **defaults)

    return manifest


def _check_for_unknown_keys(allowed: Iterable[str], user: Iterable[str]) -> None:
    if unknown_keys := (set(user) - set(allowed)):
        raise UnknownKeyError(unknown_keys)
