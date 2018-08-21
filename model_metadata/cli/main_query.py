#! /usr/bin/env python
from __future__ import print_function

import os
import sys
import argparse
import textwrap

from ..modelmetadata import ModelMetadata
from ..errors import MissingSectionError, MissingValueError


def configure_parser_mmd_query(sub_parsers=None):
    help = "get info about a model"

    example = textwrap.dedent(
        """

    Examples:

    mmd query Child --var=run

    """
    )
    if sub_parsers is None:
        p = argparse.ArgumentParser(
            description=help, fromfile_prefix_chars="@", epilog=example
        )
    else:
        p = sub_parsers.add_parser("query", help=help, description=help, epilog=example)
    p.add_argument("model", type=str, help="model to query")
    p.add_argument(
        "--var", action="append", type=str, help="name of variable or section"
    )

    p.set_defaults(func=execute)

    return p


def execute(args):
    if os.path.isdir(args.model):
        path_to_mmd = args.model
    else:
        path_to_mmd = os.path.join(sys.prefix, "share", "csdms", args.model)
    if not os.path.isdir(path_to_mmd):
        raise MetadataNotFoundError(args.model)

    if args.var:
        meta = ModelMetadata(path_to_mmd)
        for var in args.var:
            try:
                print(meta.get(var), file=sys.stdout)
            except MissingSectionError as err:
                print("{0}: Missing section".format(err.name), file=sys.stderr)
            except MissingValueError as err:
                print("{0}: Missing value".format(err.name), file=sys.stderr)


def main():
    import argparse

    p = configure_parser_mmd_query()

    args = p.parse_args()

    args.func(args)
