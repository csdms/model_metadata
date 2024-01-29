#! /usr/bin/env python
from __future__ import annotations

import os
import shutil
from typing import Any

from jinja2 import Environment
from jinja2 import FileSystemLoader as _FileSystemLoader
from model_metadata._utils import as_cwd
from model_metadata._utils import is_text_file
from model_metadata.find import find_model_data_files
from model_metadata.find import is_metadata_file
from model_metadata.model_data_files import FileTemplate


class OldFileSystemLoader:
    def __init__(self, searchpath: str):
        self._base = os.path.abspath(searchpath)
        self._files = find_model_data_files(self._base)

    @property
    def base(self) -> str:
        return self._base

    @property
    def sources(self) -> tuple[str, ...]:
        return tuple(self._files)

    def stage_all(self, destdir: str, **kwds: dict[str, Any]) -> tuple[str, ...]:
        sources = (os.path.relpath(fn, self.base) for fn in self.sources)
        with as_cwd(destdir, create=True):
            manifest = (
                p for src in sources if (p := self.stage(src, **kwds)) is not None
            )
        return tuple(manifest)

    def stage(self, relpath: str, **kwds: dict[str, Any]) -> str | None:
        src = os.path.join(self.base, relpath)
        if os.path.isdir(src):
            os.makedirs(os.path.realpath(relpath), exist_ok=True)
            staged_file = None
        else:
            staged_file = self.render_source(relpath, **kwds)
        return staged_file

    def render_source(self, relpath: str, **kwds: dict[str, Any]) -> str | None:
        src = os.path.join(self.base, relpath)

        if os.path.isdir(src):
            os.makedirs(os.path.realpath(relpath), exist_ok=True)
            staged_file = None
        elif is_text_file(src):
            staged_file = FileTemplate(src).to_file(relpath, **kwds)
        else:
            shutil.copy2(src, relpath)
            staged_file = relpath
        return staged_file


class FileSystemLoader:
    def __init__(self, searchpath: str):
        self._base = os.path.abspath(searchpath)

    def stage_all(self, destdir: str, **defaults: dict[str, Any]) -> tuple[str, ...]:
        env = Environment(loader=_FileSystemLoader(self._base))
        manifest = env.list_templates(filter_func=lambda f: not is_metadata_file(f))

        os.makedirs(destdir, exist_ok=True)
        for fname in manifest:
            src_file = os.path.join(self._base, fname)
            dst_file = os.path.join(destdir, fname)

            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            if is_text_file(src_file):
                with open(dst_file, "w") as fp:
                    fp.write(env.get_template(fname).render(**defaults))
            else:
                shutil.copy2(src_file, dst_file)

        return tuple(manifest)
