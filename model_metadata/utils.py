#! /usr/bin/env python
import os
import sys

from jinja2 import FileSystemLoader, Environment
from scripting.contexts import cd
from scripting import cp, ln_s


def install_mmd(path, dest, develop=False, silent=True, dry_run=False,
                clobber=False):
    templates = Environment(loader=FileSystemLoader(path)).list_templates()
    for fname in templates:
        if develop:
            install = ln_s
        else:
            install = cp
        install(os.path.join(path, fname), os.path.join(dest, fname),
                silent=silent, dry_run=dry_run, create_dirs=True,
                clobber=clobber)


def get_cmdclass(paths, cmdclass=None):

    cmdclass = {} if cmdclass is None else cmdclass.copy()

    if 'setuptools' in sys.modules:
        from setuptools.command.install import install as _install
        from setuptools.command.develop import develop as _develop
    else:
        from distutils.command.install import install as _install
        from distutils.command.develop import develop as _develop

    sharedir = os.path.join(sys.prefix, 'share')
    class install(_install):
        def run(self):
            _install.run(self)
            for name, path in paths:
                name = name.split(':')[-1]
                install_mmd(os.path.abspath(path),
                            os.path.join(sharedir, 'csdms', name),
                            silent=False,
                            clobber=True,
                            develop=False)


    class develop(_develop):
        def run(self):
            _develop.run(self)
            for name, path in paths:
                name = name.split(':')[-1]
                install_mmd(os.path.abspath(path),
                            os.path.join(sharedir, 'csdms', name),
                            silent=False,
                            clobber=True,
                            develop=True)

    cmdclass['install'] = install
    cmdclass['develop'] = develop

    return cmdclass


def get_entry_points(components, entry_points=None):
    entry_points = {} if entry_points is None else entry_points

    pymt_plugins = entry_points.get('pymt.plugins', [])

    for entry_point, _ in components:
        pymt_plugins.append(entry_point)

    if len(pymt_plugins) > 0:
        entry_points['pymt.plugins'] = pymt_plugins

    return entry_points


