from __future__ import annotations

import contextlib
import errno
import os
import shutil
import sys
from collections.abc import Generator


@contextlib.contextmanager
def as_cwd(path: str, create: bool = True) -> Generator[None, None, None]:
    prev_cwd = os.getcwd()

    if create:
        os.makedirs(os.path.realpath(path), exist_ok=True)
    os.chdir(path)

    yield
    os.chdir(prev_cwd)


def cp(
    source: str,
    dest: str,
    dry_run: bool = False,
    clobber: bool = True,
    create_dirs: bool = False,
    silent: bool = False,
) -> None:
    """Copy file from source to destination.

    Parameters
    ----------
    source : str
        Path to source file.
    dest : str
        Path to destination directory or destination file name.
    dry_run : bool, optional
        Print what would have been done, but don't do it.
    clobber : bool, optional
        If destination file exists, overwrite it. Otherwise raise
        an exception.
    create_dirs : bool, optional
        Create intermediate directories if they don't already exist.
        Otherwise, raise an exception if a destination directory is
        missing.
    silent : bool, optional
        Supress displaying anything, except if ``dry_run`` is used.
    """
    cp_args = (source, dest)

    if not silent or dry_run:
        print(f"cp {source} {dest}", file=sys.stderr)

    if not dry_run:
        if os.path.isfile(dest) and not clobber:
            raise OSError(f"{dest}: file exists")
        elif os.path.islink(dest):
            os.remove(dest)

        with as_cwd(os.path.dirname(dest) or ".", create=create_dirs):
            pass
        shutil.copy2(*cp_args)


def ln_s(
    source: str,
    dest: str,
    dry_run: bool = False,
    clobber: bool = True,
    create_dirs: bool = False,
    silent: bool = False,
) -> None:
    """Link file from source to destination.

    Parameters
    ----------
    source : str
        Path to source file.
    dest : str
        Path to destination directory or destination file name.
    dry_run : bool, optional
        Print what would have been done, but don't do it.
    clobber : bool, optional
        If destination file exists, overwrite it. Otherwise raise
        an exception.
    create_dirs : bool, optional
        Create intermediate directories if they don't already exist.
        Otherwise, raise an exception if a destination directory is
        missing.
    silent : bool, optional
        Supress displaying anything, except if ``dry_run`` is used.
    """
    ln_args = (source, dest)

    if not silent or dry_run:
        print(f"ln -s {source} {dest}", file=sys.stderr)

    if not dry_run:
        if os.path.isfile(dest):
            if clobber:
                os.remove(dest)
            else:
                raise OSError(f"{dest}: file exists")

        with as_cwd(os.path.dirname(dest) or ".", create=create_dirs):
            pass
        os.symlink(*ln_args)
