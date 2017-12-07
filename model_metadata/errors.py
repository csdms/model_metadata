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
