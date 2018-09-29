#! /usr/bin/env python
import os
import string
import tempfile

from scripting.contexts import cd, mkdir_p


class SafeFormatter(string.Formatter):
    def get_field(self, field_name, args, kwargs):
        try:
            val = super(SafeFormatter, self).get_field(field_name, args, kwargs)
        except (KeyError, AttributeError):
            val = "{" + field_name + "}", field_name

        return val

    def format_field(self, value, spec):
        try:
            return super(SafeFormatter, self).format_field(value, spec)
        except ValueError:
            return value


class FileTemplate(object):

    _formatter = SafeFormatter()

    def __init__(self, path):
        self._path = os.path.abspath(path)
        self._head, self._tail = os.path.split(self._path)

    @property
    def path(self):
        return self._path

    @property
    def tail(self):
        return self._tail

    def render(self, **kwds):
        with open(self.path, "r") as fp:
            template = fp.read()
        return self._formatter.format(template, **kwds)

    def to_file(self, dest, **kwds):
        if dest.endswith(os.path.sep):
            mkdir_p(dest)
            dest = os.path.join(dest, self.tail)

        (base, ext) = os.path.splitext(dest)
        if ext == ".tmpl":
            dest = base

        with open(dest, "w") as fp:
            fp.write(self.render(**kwds))

        return dest

    @staticmethod
    def format(file_like, **kwds):
        try:
            template = file_like.read()
        except AttributeError:
            template = file_like
        return sub_parameters(template, **kwds)

    @staticmethod
    def write(file_like, dest, **kwds):
        if os.path.isfile(dest):
            if file_like:
                raise ValueError("{dest}: destination already exists".format(dest=dest))
            else:
                return dest
        elif os.path.isdir(dest):
            fid, dest = tempfile.mkstemp(dir=dest, prefix=".", suffix=".txt")
            os.close(fid)

        with open(dest, "w") as fp:
            fp.write(FileTemplate.format(file_like, **kwds))

        return dest


def format_template_file(src, dest, **kwds):
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

    # if os.path.isdir(dest):
    if dest.endswith(os.path.sep):
        mkdir_p(dest)
        dest = os.path.join(dest, fname)

    (base, ext) = os.path.splitext(dest)
    if ext == ".tmpl":
        dest = base

    with cd(srcdir):
        with open(fname, "r") as fp:
            template = fp.read()

        with open(dest, "w") as fp:
            fp.write(sub_parameters(template, **kwds))


def sub_parameters(string, **kwds):
    formatter = SafeFormatter()
    return formatter.format(string, **kwds)
