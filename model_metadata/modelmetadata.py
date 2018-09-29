#! /usr/bin/env python
import os
import warnings

import six
import yaml

from .errors import MissingSectionError, MissingValueError
from .load import load_yaml_file
from .find import find_metadata_files
from .model_info import ModelInfo
from .model_parameter import parameter_from_dict, setup_yaml_with_canonical_dict

setup_yaml_with_canonical_dict()


def normalize_run_section(run):
    normed = {"config_file": {"path": None, "contents": None}}

    if run is None:
        pass
    elif "config_file" not in run:
        pass
    elif isinstance(run["config_file"], six.string_types):
        normed["config_file"]["path"] = run["config_file"]
    else:
        for key in ("path", "contents"):
            normed["config_file"][key] = run["config_file"].get(key, None)

    return normed


class ModelMetadata(object):

    SECTIONS = ("api", "info", "parameters", "run")

    def __init__(self, path):
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
