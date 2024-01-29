#! /usr/bin/env python
from __future__ import annotations

import contextlib
import os
import pathlib
import sys
import warnings
from typing import Any

if sys.version_info >= (3, 12):  # pragma: no cover (PY12+)
    from importlib.resources import files
else:  # pragma: no cover (<PY312)
    from importlib_resources import files
import yaml
from model_metadata.errors import BadEntryPointError
from model_metadata.errors import MetadataNotFoundError
from model_metadata.errors import MissingSectionError
from model_metadata.errors import MissingValueError
from model_metadata.find import find_metadata_files
from model_metadata.load import load_meta_section
from model_metadata.model_info import ModelInfo
from model_metadata.model_parameter import parameter_from_dict
from model_metadata.model_parameter import setup_yaml_with_canonical_dict
from model_metadata._utils import load_component
from model_metadata._utils import parse_entry_point


setup_yaml_with_canonical_dict()


def normalize_run_section(run: dict[str, Any] | None) -> dict[str, Any]:
    # normed = {"config_file": {"path": None, "contents": None}}
    normed: dict[str, Any] = {"config_file": {}}

    if (run is None) or ("config_file" not in run):
        pass
    elif isinstance(run["config_file"], str):
        normed["config_file"]["path"] = run["config_file"]
    else:
        for key in ("path", "contents"):
            normed["config_file"][key] = run["config_file"].get(key)
    normed["config_file"].setdefault("path", None)
    normed["config_file"].setdefault("contents", None)

    return normed


class ModelMetadata:
    SECTIONS = ("api", "info", "parameters", "run")

    def __init__(self, path: str):
        # self._path = find(path)
        self._path = os.path.abspath(path)

        self._files = find_metadata_files(self._path)
        self._meta = self.load_all()

        self._meta["info"].setdefault("name", self.api["name"])
        self._meta["info"] = ModelInfo.norm(self._meta["info"])
        self._meta["run"] = normalize_run_section(self._meta.get("run"))

        params = self._meta.pop("parameters", {})
        self._meta["parameters"] = {}

        public = (name for name in params if not name.startswith("_"))
        for name in public:
            try:
                param = parameter_from_dict(params[name]).as_dict()
            except ValueError:
                raise ValueError(f"{name}: unable to load parameter")
            else:
                self._meta["parameters"][name] = param

        private = (name for name in params if name.startswith("_"))
        for name in private:
            warnings.warn(
                f"{name}: ignoring private attribute in parameters section",
                stacklevel=2,
            )

    @classmethod
    def from_obj(cls, obj: type) -> ModelMetadata:
        return cls(ModelMetadata.find(obj))

    @staticmethod
    def search_paths(model: str | pathlib.Path | type) -> tuple[str, ...]:
        """List of paths to search in looking for a model's metadata.

        Parameters
        ----------
        model : path, str or object
            The model is interpreted either as a path to a folder that
            contains metadata, the name of a model component, or a
            model object.

        Returns
        -------
        list of Paths
            Paths to search for metadata.
        """
        if isinstance(model, (str, pathlib.Path)):
            model = str(model)
            with contextlib.suppress(BadEntryPointError):
                model = load_component(*parse_entry_point(model))

        paths = []

        def _model_module(model: type) -> str:
            try:
                return model.__module__
            except AttributeError:
                return model.__class__.__module__

        def _model_name(model: type) -> str:
            try:
                return model.__name__
            except AttributeError:
                return model.__class__.__name__

        if not isinstance(model, str) and hasattr(model, "METADATA"):
            path_to_module = str(files(_model_module(model)))

            try:
                path_to_metadata = model.METADATA
                # path_to_metadata = pathlib.Path(model.METADATA)
            except TypeError:
                warnings.warn(
                    "object has METADATA attribute but it is not path-like",
                    stacklevel=2,
                )
            else:
                paths.append(
                    os.path.realpath(os.path.join(path_to_module, path_to_metadata))
                )

        paths.append(model if isinstance(model, str) else _model_name(model))

        # try:
        #     paths.append(pathlib.Path(model))
        # except TypeError:
        #     paths.append(pathlib.Path(_model_name(model)))

        # sharedir = pathlib.Path(sys.prefix, "share", "csdms")
        sharedir = os.path.join(sys.prefix, "share", "csdms")

        paths.append(
            os.path.join(
                sharedir, model if isinstance(model, str) else _model_name(model)
            )
        )

        # try:
        #     paths.append(sharedir / model)
        # except TypeError:
        #     paths.append(sharedir / _model_name(model))

        return tuple(os.path.normpath(p) for p in paths)
        # return tuple(paths)

    @staticmethod
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
        for p in ModelMetadata.search_paths(model):
            # if p.is_dir():
            if os.path.isdir(p):
                return p
        raise MetadataNotFoundError(str(model))

    def get(self, key: str) -> Any:
        """Get a metadata value with dotted notation.

        Parameters
        ----------
        key : str
            Name of a value or section in dotted notation. For example,
            `run.config_file.path`.
        """
        val, section = self._meta, ""
        for name in key.split("."):
            section = ".".join([section, name])
            try:
                val = val[name]
            except KeyError:
                if key.endswith(name):
                    raise MissingValueError(section)
                else:
                    raise MissingSectionError(section)
            except TypeError:
                raise MissingValueError(section)

        return val

    @staticmethod
    def format(value: Any) -> str:
        return yaml.safe_dump(value)

    @property
    def base(self) -> str:
        return self._path

    @property
    def meta(self) -> dict[str, Any]:
        return self._meta

    @property
    def name(self) -> str:
        return self.info["name"]

    @property
    def api(self) -> dict[str, Any]:
        return self._meta.get("api", {})

    @property
    def info(self) -> dict[str, Any]:
        return self._meta.get("info", {})

    @property
    def parameters(self) -> dict[str, Any]:
        return self._meta.get("parameters", {})

    @property
    def run(self) -> dict[str, Any]:
        return self._meta["run"]

    def dump(self) -> str:
        return yaml.safe_dump(self.meta)

    def dump_section(self, section: str | None = None) -> str:
        if section:
            return yaml.safe_dump({section: self.meta.get(section, {})})
        else:
            return self.dump()

    def load_section(self, section: str) -> dict[str, Any]:
        return load_meta_section(self.base, section)

    def load_all(self) -> dict[str, Any]:
        return {section: self.load_section(section) for section in self.SECTIONS}
