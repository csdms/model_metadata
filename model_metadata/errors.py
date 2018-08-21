#! /usr/bin/env python


class ModelMetadataError(Exception):

    """Base error for model_metadata package."""

    pass


class MetadataNotFoundError(ModelMetadataError):

    """Raise if metadata cannot be found."""

    def __init__(self, path_to_metadata):
        self._path = path_to_metadata

    def __str__(self):
        return self._path


class MissingSectionError(ModelMetadataError):

    """Raise if a section in not found in the metadata."""

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self._name


class MissingValueError(ModelMetadataError):

    """Raise if a value is not found in a metadata section."""

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self._name
