#! /usr/bin/env python
from __future__ import print_function

import os
import sys
import argparse
import textwrap
import shutil

from jinja2 import Environment, FileSystemLoader
from scripting.contexts import cd

from ..model_setup import FileSystemLoader, OldFileSystemLoader
from ..model_setup import is_text_file
from ..modelmetadata import ModelMetadata
from ..metadata.find import is_metadata_file
from ..errors import MetadataNotFoundError


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
        "--manifest-file",
        type=str,
        help="write manifest of staged files to a file instead of the screen",
    )
    p.add_argument(
        "--old-style-templates", action="store_true", help="use old-style templates"
    )

    p.set_defaults(func=execute)

    return p


def execute(args):
    if os.path.isdir(args.model):
        mmd = args.model
    else:
        mmd = os.path.join(sys.prefix, "share", "csdms", args.model)

    if not os.path.isdir(mmd):
        raise MetadataNotFoundError(args.model)

    defaults = dict()
    meta = ModelMetadata(mmd)
    for param, item in meta.parameters.items():
        defaults[param] = item["value"]["default"]

    if args.old_style_templates:
        manifest = OldFileSystemLoader(mmd).stage_all(args.dest, **defaults)
    else:
        manifest = FileSystemLoader(mmd).stage_all(args.dest, **defaults)
    manifest = os.linesep.join(manifest)

    if args.manifest_file is not None:
        with open(args.manifest_file, "w") as fp:
            print(manifest, file=fp)
    elif not args.quiet:
        print(manifest, file=sys.stdout)


def main():
    import argparse

    p = configure_parser_mmd_stage()

    args = p.parse_args()

    args.func(args)
