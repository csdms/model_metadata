#! /usr/bin/env python
from __future__ import print_function

import os
import sys
import argparse
import textwrap
import shutil

from jinja2 import Environment, FileSystemLoader
from scripting.contexts import cd

from ..model_setup import FileSystemLoader as OldFileSystemLoader
from ..model_setup import is_text_file
from ..modelmetadata import ModelMetadata
from ..metadata.find import is_metadata_file
from ..errors import MetadataNotFoundError


def configure_parser_mmd_stage(sub_parsers=None):
    help = "stage model data files"

    example = textwrap.dedent("""

    Examples:

    mmd stage Child

    """)
    if sub_parsers is None:
        p = argparse.ArgumentParser(
            description=help,
            fromfile_prefix_chars='@',
            epilog=example,
        )
    else:
        p = sub_parsers.add_parser(
            'stage',
            help=help,
            description=help,
            epilog=example,
        )
    p.add_argument(
        'model',
        help='model to stage',
    )
    p.add_argument(
        'dest',
        help='where to stage files',
    )
    p.add_argument(
        '--jinja',
        action='store_true',
        help='use jinja templates',
    )

    p.set_defaults(func=execute)

    return p


def execute(args):
    if os.path.isdir(args.model):
        mmd = args.model
    else:
        mmd = os.path.join(sys.prefix, 'share', 'csdms', args.model)

    if not os.path.isdir(mmd):
        raise MetadataNotFoundError(args.model)

    defaults = dict()
    for param, item in ModelMetadata(mmd).parameters.items():
        defaults[param] = item['value']['default']

    if args.jinja:
        env = Environment(loader=FileSystemLoader(mmd))
        with cd(args.dest):
            for fname in env.list_templates(filter_func=lambda f: not is_metadata_file(f)):
                with cd(os.path.dirname(fname) or '.', create=True):
                    pass
                if is_text_file(os.path.join(mmd, fname)):
                    with open(fname, 'w') as fp:
                        fp.write(env.get_template(fname).render(**defaults))
                else:
                    shutil.copy2(os.path.join(mmd, fname), fname)
    else:
        OldFileSystemLoader(mmd).stage_all(args.dest, **defaults)


def main():
    import argparse

    p = configure_parser_mmd_stage()

    args = p.parse_args()

    args.func(args)
