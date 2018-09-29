#! /usr/bin/env python
from __future__ import print_function

import argparse
import os
import sys
import textwrap

from ..find import find_metadata_files
from ..model_setup import FileSystemLoader


def configure_parser_mmd_find(sub_parsers=None):
    help = "Find model metadata"

    example = textwrap.dedent(
        """

    Examples:

    mmd find

    """
    )
    if sub_parsers is None:
        p = argparse.ArgumentParser(
            description=help, fromfile_prefix_chars="@", epilog=example
        )
    else:
        p = sub_parsers.add_parser("find", help=help, description=help, epilog=example)
    p.add_argument("name", help="name of model")
    p.add_argument("--data", action="store_true", help="find only data files")

    p.set_defaults(func=execute)

    return p


def execute(args):
    search_path = os.path.join(sys.prefix, "share", "csdms", args.name)
    # sources = FileSystemLoader(args.path).sources
    if args.data:
        sources = FileSystemLoader(search_path).sources
    else:
        sources = find_metadata_files(search_path)
    for path in sources:
        print(path)


def main():
    p = configure_parser_mmd_find()

    args = p.parse_args()

    args.func(args)
