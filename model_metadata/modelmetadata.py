#! /usr/bin/env python
import os

import yaml

from .metadata.find import find_metadata_files
from .metadata.load import load_yaml_file
from .model_parameter import (ModelParameter, setup_yaml_with_canonical_dict,
                              parameter_from_dict)
from .model_info import ModelInfo


setup_yaml_with_canonical_dict()

class ModelMetadata(object):

    SECTIONS = ('api', 'info', 'parameters', 'run')

    def __init__(self, path):
        self._path = os.path.abspath(path)
        self._files = find_metadata_files(self._path)
        self._meta = self.load_all()

        self._meta['info'].setdefault('name', self.api['name'])
        self._meta['info'] = ModelInfo.norm(self._meta['info'])

        params = self._meta.pop('parameters', {})
        self._meta['parameters'] = {}
        for name, p in params.items():
            try:
                self._meta['parameters'][name] = parameter_from_dict(p).as_dict()
            except ValueError:
                raise ValueError('{name}: unable to load paramter'.format(name=name))

    @property
    def base(self):
        return self._path

    @property
    def meta(self):
        return self._meta

    @property
    def api(self):
        return self._meta.get('api', {})

    @property
    def info(self):
        return self._meta.get('info', {})

    @property
    def parameters(self):
        return self._meta.get('parameters', {})

    @property
    def run(self):
        return self._meta.get('run', {})

    def dump(self):
        return yaml.safe_dump(self.meta)

    def dump_section(self, section=None):
        if section:
            return yaml.safe_dump({
                section: self.meta.get(section, {})
            })
        else:
            return self.dump()

    def load_section(self, section):
        meta_path = os.path.join(self.base, 'meta.yaml')
        meta = load_yaml_file(meta_path) or {}

        try:
            meta_section = meta[section]
        except KeyError:
            section_path = os.path.join(
                self.base, '{section}.yaml'.format(section=section))
            meta_section = load_yaml_file(section_path) or {}

        return meta_section

    def load_all(self):
        meta = {}
        for section in self.SECTIONS:
            meta[section] = self.load_section(section)
        return meta