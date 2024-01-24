#! /usr/bin/env python
from __future__ import annotations


class ModelMetadataError(Exception):

    """Base error for model_metadata package."""

    pass


class MetadataNotFoundError(ModelMetadataError):

    """Raise if metadata cannot be found."""

    def __init__(self, path_to_metadata: str):
        self._path = path_to_metadata

    def __str__(self) -> str:
        return self._path


class MissingSectionError(ModelMetadataError):

    """Raise if a section in not found in the metadata."""

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return self._name


class MissingValueError(ModelMetadataError):

    """Raise if a value is not found in a metadata section."""

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return self._name
