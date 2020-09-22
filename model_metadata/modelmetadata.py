#! /usr/bin/env python
import importlib
import os
import pathlib
import sys
import warnings

import pkg_resources
import yaml

from .errors import MetadataNotFoundError, MissingSectionError, MissingValueError
from .find import find_metadata_files
from .load import load_yaml_file
from .model_info import ModelInfo
from .model_parameter import parameter_from_dict, setup_yaml_with_canonical_dict

setup_yaml_with_canonical_dict()


def normalize_run_section(run):
    normed = {"config_file": {"path": None, "contents": None}}

    if run is None:
        pass
    elif "config_file" not in run:
        pass
    elif isinstance(run["config_file"], str):
        normed["config_file"]["path"] = run["config_file"]
    else:
        for key in ("path", "contents"):
            normed["config_file"][key] = run["config_file"].get(key, None)

    return normed


def _load_component(entry_point):
    if "" not in sys.path:
        sys.path.append("")

    module_name, cls_name = entry_point.split(":")

    component = None
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        raise
    else:
        try:
            component = module.__dict__[cls_name]
        except KeyError:
            raise ImportError(cls_name)

    return component


class ModelMetadata:

    SECTIONS = ("api", "info", "parameters", "run")

    def __init__(self, path):
        # self._path = find(path)
        self._path = os.path.abspath(path)

        self._files = find_metadata_files(self._path)
        self._meta = self.load_all()

        self._meta["info"].setdefault("name", self.api["name"])
        self._meta["info"] = ModelInfo.norm(self._meta["info"])
        self._meta["run"] = normalize_run_section(self._meta.get("run", None))

        params = self._meta.pop("parameters", {})
        self._meta["parameters"] = {}

        public = (name for name in params if not name.startswith("_"))
        for name in public:
            try:
                param = parameter_from_dict(params[name]).as_dict()
            except ValueError:
                raise ValueError("{name}: unable to load parameter".format(name=name))
            else:
                self._meta["parameters"][name] = param

        private = (name for name in params if name.startswith("_"))
        for name in private:
            warnings.warn(
                "{name}: ignoring private attribute in parameters section".format(
                    name=name
                )
            )

    @classmethod
    def from_obj(cls, obj):
        path_to_metadata = ModelMetadata.find(obj)
        return cls(path_to_metadata)

    @staticmethod
    def search_paths(model):
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
        if isinstance(model, str) and ":" in model:
            try:
                model = _load_component(model)
            except ImportError:
                pass

        paths = []

        def _model_module(model):
            try:
                return model.__module__
            except AttributeError:
                return model.__class__.__module__

        def _model_name(model):
            try:
                return model.__name__
            except AttributeError:
                return model.__class__.__name__

        if hasattr(model, "METADATA"):
            path_to_module = pkg_resources.resource_filename(_model_module(model), "")

            try:
                path_to_metadata = pathlib.Path(model.METADATA)
            except TypeError:
                warnings.warn("object has METADATA attribute but it is not path-like")
            else:
                paths.append((path_to_module / path_to_metadata).resolve())

        try:
            paths.append(pathlib.Path(model))
        except TypeError:
            paths.append(pathlib.Path(_model_name(model)))

        sharedir = pathlib.Path(sys.prefix, "share", "csdms")

        try:
            paths.append(sharedir / model)
        except TypeError:
            paths.append(sharedir / _model_name(model))

        return paths

    @staticmethod
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
        for p in ModelMetadata.search_paths(model):
            if p.is_dir():
                return p
        raise MetadataNotFoundError(str(model))

    def get(self, key):
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
    def format(value):
        return yaml.safe_dump(value)

    @property
    def base(self):
        return self._path

    @property
    def meta(self):
        return self._meta

    @property
    def name(self):
        return self.info["name"]

    @property
    def api(self):
        return self._meta.get("api", {})

    @property
    def info(self):
        return self._meta.get("info", {})

    @property
    def parameters(self):
        return self._meta.get("parameters", {})

    @property
    def run(self):
        return self._meta["run"]

    def dump(self):
        return yaml.safe_dump(self.meta)

    def dump_section(self, section=None):
        if section:
            return yaml.safe_dump({section: self.meta.get(section, {})})
        else:
            return self.dump()

    def load_section(self, section):
        meta_path = os.path.join(self.base, "meta.yaml")
        meta = load_yaml_file(meta_path) or {}

        try:
            meta_section = meta[section]
        except KeyError:
            section_path = os.path.join(
                self.base, "{section}.yaml".format(section=section)
            )
            meta_section = load_yaml_file(section_path) or {}

        return meta_section

    def load_all(self):
        meta = {}
        for section in self.SECTIONS:
            meta[section] = self.load_section(section)
        return meta
