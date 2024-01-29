#! /usr/bin/env python
from __future__ import annotations

import io
import os
import string
import tempfile
from collections.abc import Mapping
from collections.abc import Sequence
from typing import Any


class SafeFormatter(string.Formatter):
    def get_field(
        self, field_name: str, args: Sequence[str], kwargs: Mapping[str, Any]
    ) -> tuple[str, str]:
        try:
            val = super().get_field(field_name, args, kwargs)
        except (KeyError, AttributeError):
            val = "{" + field_name + "}", field_name

        return val

    def format_field(self, value: str, spec: str) -> str:
        try:
            return super().format_field(value, spec)
        except ValueError:
            return value


class FileTemplate:
    _formatter = SafeFormatter()

    def __init__(self, path: str):
        self._path = os.path.abspath(path)
        self._head, self._tail = os.path.split(self._path)

    @property
    def path(self) -> str:
        return self._path

    @property
    def tail(self) -> str:
        return self._tail

    def render(self, **kwds: dict[str, Any]) -> str:
        with open(self.path) as fp:
            template = fp.read()
        return self._formatter.format(template, **kwds)

    def to_file(self, dest: str, **kwds: dict[str, Any]) -> str:
        if dest.endswith(os.path.sep):
            os.makedirs(os.path.realpath(dest), exist_ok=True)
            dest = os.path.join(dest, self.tail)

        (base, ext) = os.path.splitext(dest)
        if ext == ".tmpl":
            dest = base

        with open(dest, "w") as fp:
            fp.write(self.render(**kwds))

        return dest

    @staticmethod
    def format(file_like: io.TextIOBase | str, **kwds: dict[str, Any]) -> str:
        if isinstance(file_like, str):
            template = file_like
        else:
            template = file_like.read()
        return sub_parameters(template, **kwds)

    @staticmethod
    def write(file_like: io.TextIOBase, dest: str, **kwds: dict[str, Any]) -> str:
        if os.path.isfile(dest):
            if file_like:
                raise ValueError(f"{dest}: destination already exists")
            else:
                return dest
        elif os.path.isdir(dest):
            fid, dest = tempfile.mkstemp(dir=dest, prefix=".", suffix=".txt")
            os.close(fid)

        with open(dest, "w") as fp:
            fp.write(FileTemplate.format(file_like, **kwds))

        return dest


def format_template_file(src: str, dest: str, **kwds: dict[str, Any]) -> None:
    """Substitute values into a template file.

    Parameters
    ----------
    src : str
        Path to a template file.
    dest : str
        Path to output file that will contain the substitutions.
    """
    (srcdir, fname) = os.path.split(src)
    dest = os.path.abspath(dest)

    if dest.endswith(os.path.sep):
        os.makedirs(os.path.realpath(dest), exist_ok=True)
        dest = os.path.join(dest, fname)

    (base, ext) = os.path.splitext(dest)
    if ext == ".tmpl":
        dest = base

    with open(src) as fp:
        template = fp.read()

    with open(dest, "w") as fp:
        fp.write(sub_parameters(template, **kwds))


def sub_parameters(string: str, **kwds: dict[str, Any]) -> str:
    formatter = SafeFormatter()
    return formatter.format(string, **kwds)
