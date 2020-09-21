import contextlib
import errno
import os
import shutil
import sys


@contextlib.contextmanager
def as_cwd(path, create=True):
    prev_cwd = os.getcwd()

    if create:
        mkdir_p(path)
    os.chdir(path)

    yield
    os.chdir(prev_cwd)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def cp(source, dest, dry_run=False, clobber=True, create_dirs=False, silent=False):
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
            raise OSError("{0}: file exists".format(dest))
        elif os.path.islink(dest):
            os.remove(dest)

        with as_cwd(os.path.dirname(dest) or ".", create=create_dirs):
            pass
        shutil.copy2(*cp_args)


def ln_s(source, dest, dry_run=False, clobber=True, create_dirs=False, silent=False):
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
        # status("ln -s {0} {1}".format(*ln_args))

    if not dry_run:
        if os.path.isfile(dest):
            if clobber:
                os.remove(dest)
            else:
                raise OSError("{0}: file exists".format(dest))

        with as_cwd(os.path.dirname(dest) or ".", create=create_dirs):
            pass
        os.symlink(*ln_args)
