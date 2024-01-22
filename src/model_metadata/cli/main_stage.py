#! /usr/bin/env python
from __future__ import print_function

import argparse
import os
import sys
import textwrap

from ..api import stage


def configure_parser_mmd_stage(sub_parsers=None):
    help = "stage model data files"

    example = textwrap.dedent(
        """

    Examples:

    mmd stage Child

    """
    )
    if sub_parsers is None:
        p = argparse.ArgumentParser(
            description=help, fromfile_prefix_chars="@", epilog=example
        )
    else:
        p = sub_parsers.add_parser("stage", help=help, description=help, epilog=example)
    p.add_argument("model", help="model to stage")
    p.add_argument("dest", help="where to stage files")
    p.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="supress printing the manifest to the screen",
    )
    p.add_argument(
        "--old-style-templates", action="store_true", help="use old-style templates"
    )

    p.set_defaults(func=execute)

    return p


def execute(args):
    manifest = stage(
        args.model, dest=args.dest, old_style_templates=args.old_style_templates
    )
    if not args.quiet:
        print(os.linesep.join(manifest), file=sys.stdout)


def main():
    p = configure_parser_mmd_stage()

    args = p.parse_args()

    args.func(args)
