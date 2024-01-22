#! /usr/bin/env python
from __future__ import print_function

import argparse
import os
import sys
import textwrap

from ..modelmetadata import ModelMetadata


def configure_parser_mmd_dump(sub_parsers=None):
    help = "get info about a model"

    example = textwrap.dedent(
        """

    Examples:

    mmd dump Child

    """
    )
    if sub_parsers is None:
        p = argparse.ArgumentParser(
            description=help, fromfile_prefix_chars="@", epilog=example
        )
    else:
        p = sub_parsers.add_parser("dump", help=help, description=help, epilog=example)
    p.add_argument("model", type=str, help="model to query")
    p.add_argument(
        "-s", "--section", action="append", type=str, help="name of metadata section"
    )

    p.set_defaults(func=execute)

    return p


def execute(args):
    if os.path.isdir(args.model):
        path_to_mmd = args.model
    else:
        path_to_mmd = os.path.join(sys.prefix, "share", "csdms", args.model)

    if args.section:
        for name in args.section:
            print(ModelMetadata(path_to_mmd).dump_section(name))
    else:
        print(ModelMetadata(path_to_mmd).dump())


def main():
    p = configure_parser_mmd_dump()

    args = p.parse_args()

    args.func(args)
