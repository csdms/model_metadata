from __future__ import annotations
import contextlib
import os
from collections.abc import Generator


@contextlib.contextmanager
def as_cwd(path: str, create: bool = True) -> Generator[None, None, None]:
    prev_cwd = os.getcwd()

    if create:
        os.makedirs(os.path.realpath(path), exist_ok=True)
    os.chdir(path)

    yield
    os.chdir(prev_cwd)
