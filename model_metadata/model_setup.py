#! /usr/bin/env python
import errno
import os
import shutil

from binaryornot.check import is_binary
from scripting.contexts import cd

from .find import find_model_data_files
from .model_data_files import FileTemplate

TEXT_CHARACTERS = "".join(list(map(chr, range(32, 127))) + list("\n\r\t\b"))


def is_text_file(fname, block=1024):
    """Check if a file is text or binary.

    Parameters
    ----------
    fname : str
        Path to file to check.
    block : int, optional
        Number of characters to read to determine if the file is text
        or binary.

    Returns
    -------
    bool
        ``True`` if the file is probably text, otherwise ``False``.
    """
    with open(fname, "rb") as fp:
        return is_text(fp.read(block))


def is_text(buff):
    """Check if a buffer is text or binary.

    Parameters
    ----------
    buff : str
        Buffer of characters to check.

    Returns
    -------
    bool
        ``True`` if the buffer is probably text, otherwise ``False``.
    """
    if "\0" in buff:
        return False

    if len(buff) == 0:
        return True

    # bin_chars = buff.translate(NULL_TRANS, TEXT_CHARACTERS)
    bin_chars = buff.translate(None, TEXT_CHARACTERS)

    if len(bin_chars) > len(buff) * 0.3:
        return False

    return True


def mkdir_p(path):
    """Make a directory along with any parents."""
    if not path:
        return

    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class OldFileSystemLoader(object):
    def __init__(self, searchpath):
        self._base = os.path.abspath(searchpath)
        self._files = find_model_data_files(self._base)

    @property
    def base(self):
        return self._base

    @property
    def sources(self):
        return tuple(self._files)

    def stage_all(self, destdir, **kwds):
        sources = (os.path.relpath(fn, self.base) for fn in self.sources)
        manifest = []
        with cd(destdir, create=True):
            for relpath in sources:
                relpath = self.stage(relpath, **kwds)
                if relpath:
                    manifest.append(relpath)
        return manifest

    def stage(self, relpath, **kwds):
        src = os.path.join(self.base, relpath)
        if os.path.isdir(src):
            mkdir_p(relpath)
            staged_file = None
        else:
            staged_file = self.render_source(relpath, **kwds)
        return staged_file

    def render_source(self, relpath, **kwds):
        src = os.path.join(self.base, relpath)

        if os.path.isdir(src):
            mkdir_p(relpath)
            staged_file = None
        elif is_binary(src):
            shutil.copy2(src, relpath)
            staged_file = relpath
        else:
            staged_file = FileTemplate(src).to_file(relpath, **kwds)
        return staged_file


class FileSystemLoader(object):
    def __init__(self, searchpath):
        self._base = os.path.abspath(searchpath)

    def stage_all(self, destdir, **defaults):
        from jinja2 import Environment, FileSystemLoader
        from .find import is_metadata_file
        from binaryornot.check import is_binary

        env = Environment(loader=FileSystemLoader(self._base))
        manifest = env.list_templates(filter_func=lambda f: not is_metadata_file(f))
        with cd(destdir):
            for fname in manifest:
                with cd(os.path.dirname(fname) or ".", create=True):
                    pass
                # if is_text_file(os.path.join(self._base, fname)):
                if not is_binary(os.path.join(self._base, fname)):
                    with open(fname, "w") as fp:
                        fp.write(env.get_template(fname).render(**defaults))
                else:
                    shutil.copy2(os.path.join(self._base, fname), fname)
        return manifest
