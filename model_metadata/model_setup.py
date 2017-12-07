#! /usr/bin/env python
import os
import string
import errno
import shutil

from scripting.contexts import cd

from .metadata import find_model_data_files
from .model_data_files import format_template_file, FileTemplate


TEXT_CHARACTERS = ''.join(list(map(chr, range(32, 127))) + list("\n\r\t\b"))
NULL_TRANS = string.maketrans("", "")


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
    with open(fname, 'r') as fp:
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
    if '\0' in buff:
        return False

    if len(buff) == 0:
        return True

    bin_chars = buff.translate(NULL_TRANS, TEXT_CHARACTERS)

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


class FileSystemLoader(object):

    def __init__(self, searchpath):
        self._base = searchpath
        self._files = find_model_data_files(searchpath)

    @property
    def base(self):
        return self._base

    @property
    def sources(self):
        return tuple(self._files)

    def stage_all(self, destdir, **kwds):
        sources = (os.path.relpath(fn, self.base) for fn in self.sources)
        with cd(destdir, create=True):
            for relpath in sources:
                self.stage(relpath)

    def stage(self, relpath, **kwds):
        src = os.path.join(self.base, relpath)
        if os.path.isdir(src):
            mkdir_p(relpath)
        else:
            self.render_source(relpath, **kwds)

    def render_source(self, relpath, **kwds):
        src = os.path.join(self.base, relpath)

        if os.path.isdir(src):
            mkdir_p(relpath)
        elif is_text_file(src):
            FileTemplate(src).to_file(relpath, **kwds)
        else:
            shutil.copy2(src, relpath)
