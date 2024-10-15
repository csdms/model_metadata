from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Iterable
from collections.abc import Sequence
from functools import partial
from typing import Any

from model_metadata._utils import load_component
from model_metadata._utils import parse_entry_point
from model_metadata._version import __version__
from model_metadata.api import find as _find
from model_metadata.api import query as _query
from model_metadata.api import stage as _stage
from model_metadata.errors import BadEntryPointError
from model_metadata.errors import MetadataNotFoundError
from model_metadata.errors import MissingSectionError
from model_metadata.errors import MissingValueError
from model_metadata.modelmetadata import ModelMetadata


out = partial(print, file=sys.stderr)


class FatalError(RuntimeError):
    def __init__(self, msg: str):
        self._msg = str(msg)

    def __str__(self) -> str:
        return self._msg


class ValidateEntryPoint(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        if not isinstance(values, str):
            parser.error(f"{values}: invalid entry-point: not a string")

        entry_point = values
        try:
            module_name, class_name = parse_entry_point(entry_point)
        except BadEntryPointError as error:
            parser.error(f"{entry_point}: invalid entry-point: {str(error)}")
        else:
            setattr(namespace, self.dest, (module_name, class_name))


class ValidatePathExists(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        if not isinstance(values, str):
            parser.error(f"{values}: invalid path: not a string")

        path = values

        if not os.path.isdir(path):
            parser.error(f"{path}: path does not exist")
        else:
            setattr(namespace, self.dest, path)


def main(argv: tuple[str, ...] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", action="version", version=f"model-metadata {__version__}"
    )
    subparsers = parser.add_subparsers(dest="command")

    def _add_cmd(name: str, *, help: str) -> argparse.ArgumentParser:
        parser = subparsers.add_parser(name, help=help)
        parser.add_argument(
            "-v",
            "--verbose",
            action="count",
            help="Also emit status messages to stderr.",
        )
        parser.add_argument(
            "--silent", action="store_true", help="Suppress status messages"
        )
        return parser

    find_parser = _add_cmd("find", help="find the metadata for a model")
    find_parser.add_argument("entry_point", action=ValidateEntryPoint)
    find_parser.set_defaults(func=find)

    query_parser = _add_cmd("query", help="print metadata about a model")
    query_parser.add_argument("metadata", action=ValidatePathExists)
    query_parser.set_defaults(func=query)
    vars_group = query_parser.add_mutually_exclusive_group()
    vars_group.add_argument("--var", nargs="*")
    vars_group.add_argument("--all", action="store_true")

    stage_parser = _add_cmd("stage", help="stage a model's input files")
    stage_parser.add_argument("metadata", action=ValidatePathExists)
    stage_parser.add_argument("dest")
    stage_parser.set_defaults(func=stage)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FatalError as err:
        print(err, file=sys.stderr)
        return 1


def find(args: argparse.Namespace) -> int:
    if args.verbose and not args.silent:
        out(
            f"attemting to import {args.entry_point[1]} from {args.entry_point[0]}",
            file=sys.stderr,
        )

    try:
        cls = load_component(*args.entry_point)
    except ImportError as err:
        raise FatalError(str(err))
    except ModuleNotFoundError as err:
        raise FatalError(str(err))

    if args.verbose and not args.silent:
        out(f"looking for metadata for {cls.__name__}")
    try:
        print(str(_find(cls)))
    except MetadataNotFoundError as err:
        FatalError(str(err))

    return 0


def query(args: argparse.Namespace) -> int:
    if args.all:
        vars: Iterable[str] = ModelMetadata.SECTIONS
    else:
        vars = args.var or []

    if not vars and not args.silent:
        out("nothing to query")

    values, errors = {}, {}
    for name in vars:
        try:
            value = _query(args.metadata, name)
        except MissingSectionError as err:
            errors[name] = f"{err.name}: Missing section"
        except MissingValueError as err:
            errors[name] = f"{err.name}: Missing value"
        else:
            values[name] = value

    if errors and not args.silent:
        for error in errors.values():
            out(error)
    if values:
        print(ModelMetadata.format(values))

    return len(errors)


def stage(args: argparse.Namespace) -> int:
    try:
        manifest = _stage(args.metadata, dest=args.dest)
    except MetadataNotFoundError as err:
        out(str(err))
        return 1

    if args.verbose and not args.silent:
        out(f"staged files in: {os.path.realpath(args.dest)}")
    if not manifest and not args.silent:
        out("no files to stage")

    print(os.linesep.join(manifest))

    return 0


if __name__ == "__main__":
    SystemExit(main())
