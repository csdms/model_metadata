from __future__ import annotations

import contextlib
import importlib
import keyword
import os
import re
from collections import OrderedDict
from collections.abc import Generator
from collections.abc import Sequence
from typing import Any

import yaml
from model_metadata.errors import BadEntryPointError


def parse_entry_point(entry_point: str) -> tuple[str, str]:
    try:
        module_name, class_name = entry_point.split(":")
    except ValueError:
        raise BadEntryPointError(entry_point)

    if keyword.iskeyword(module_name) or any(
        not name.isidentifier() for name in module_name.split(".")
    ):
        raise BadEntryPointError(
            entry_point, msg=f"invalid module name ({module_name})"
        )

    if not class_name.isidentifier() or keyword.iskeyword(class_name):
        raise BadEntryPointError(entry_point, msg=f"invalid class name ({class_name})")

    return (module_name, class_name)


def load_component(module_name: str, class_name: str) -> type[Any]:
    module = importlib.import_module(module_name)
    try:
        component = getattr(module, class_name)
    except AttributeError:
        raise ImportError(
            f"unable to import {class_name} from {module_name}", name=module_name
        )
    return component


@contextlib.contextmanager
def as_cwd(path: str, create: bool = True) -> Generator[None]:
    prev_cwd = os.getcwd()

    if create:
        os.makedirs(os.path.realpath(path), exist_ok=True)
    os.chdir(path)

    yield
    os.chdir(prev_cwd)


def is_text_file(path: str) -> bool:
    """Check if a file is text."""
    # https://stackoverflow.com/questions/898669
    TEXT_CHARS = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})
    with open(path, "rb") as fp:
        return not bool(fp.read(1024).translate(None, TEXT_CHARS))


def setup_yaml_with_canonical_dict() -> None:
    """https://stackoverflow.com/a/8661021"""
    yaml.add_representer(
        OrderedDict,
        lambda self, data: self.represent_mapping(
            "tag:yaml.org,2002:map", data.items()
        ),
        Dumper=yaml.SafeDumper,
    )

    def repr_ordered_dict(self: Any, data: dict[str, Any]) -> Any:
        return self.represent_mapping("tag:yaml.org,2002:map", data.items())

    yaml.add_representer(dict, repr_ordered_dict, Dumper=yaml.SafeDumper)

    def repr_dict(self: Any, data: dict[str, Any]) -> Any:
        return self.represent_mapping(
            "tag:yaml.org,2002:map", sorted(data.items(), key=lambda t: t[0])
        )

    yaml.add_representer(dict, repr_dict, Dumper=yaml.SafeDumper)

    # https://stackoverflow.com/a/45004464
    def repr_str(dumper: Any, data: str) -> Any:
        if "\n" in data:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_str(data)

    yaml.add_representer(str, repr_str, Dumper=yaml.SafeDumper)

    def repr_tuple(dumper: Any, data: Sequence[Any]) -> Any:
        return dumper.represent_sequence("tag:yaml.org,2002:seq", list(data))

    yaml.add_representer(tuple, repr_tuple, Dumper=yaml.SafeDumper)

    yaml.add_implicit_resolver(
        "tag:yaml.org,2002:float",
        re.compile(
            r"""^(?:
         [-+]?(?:[0-9][0-9_]*)\.[0-9_]*(?:[eE][-+]?[0-9]+)?
        |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
        |[-+]?\.[0-9_]+(?:[eE][-+]?[0-9]+)
        |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\.[0-9_]*
        |[-+]?\.(?:inf|Inf|INF)
        |\.(?:nan|NaN|NAN))$""",
            re.X,
        ),
        list("-+0123456789."),
        Loader=yaml.SafeLoader,
    )
