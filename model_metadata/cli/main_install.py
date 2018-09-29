#! /usr/bin/env python
from __future__ import print_function

import argparse
import os
import sys
import textwrap

from ..api import install
from ..modelmetadata import ModelMetadata


def configure_parser_mmd_install(sub_parsers=None):
    help = "install model data files"

    example = textwrap.dedent(
        """

    Examples:

    mmd install .bmi

    """
    )
    if sub_parsers is None:
        p = argparse.ArgumentParser(
            description=help, fromfile_prefix_chars="@", epilog=example
        )
    else:
        p = sub_parsers.add_parser(
            "install", help=help, description=help, epilog=example
        )
    p.add_argument("source", help="path to model metadata files")
    p.add_argument(
        "destination", nargs="?", help="path to install model metadata files into"
    )
    p.add_argument("--prefix", default=sys.prefix, help="where to install files")
    p.add_argument(
        "--develop", action="store_true", help='Install files in "development mode"'
    )
    p.add_argument("--model-name", help="name of the model")
    p.add_argument(
        "--dry-run", action="store_true", help="only display what would have been done"
    )
    p.add_argument("--silent", action="store_true", help="suppress output")

    p.set_defaults(func=execute)

    return p


def execute(args):
    if args.destination is None:
        prefix = args.prefix
        model_name = args.model_name or ModelMetadata(args.source).api["name"]
        dest = os.path.join(prefix, "share", "csdms", model_name)
    else:
        dest = args.destination

    install(
        os.path.abspath(args.source),
        os.path.abspath(dest),
        develop=args.develop,
        silent=args.silent,
        dry_run=args.dry_run,
        clobber=True,
    )


def main():
    p = configure_parser_mmd_install()

    args = p.parse_args()

    args.func(args)
