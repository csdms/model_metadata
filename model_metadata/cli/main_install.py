#! /usr/bin/env python
from __future__ import print_function

import os
import sys
import argparse
import textwrap
import shutil

from jinja2 import FileSystemLoader, Environment
from scripting.contexts import cd

# from ..model_setup import FileSystemLoader
from ..modelmetadata import ModelMetadata


def configure_parser_mmd_install(sub_parsers=None):
    help = "install model data files"

    example = textwrap.dedent("""

    Examples:

    mmd install .bmi

    """)
    if sub_parsers is None:
        p = argparse.ArgumentParser(
            description=help,
            fromfile_prefix_chars='@',
            epilog=example,
        )
    else:
        p = sub_parsers.add_parser(
            'install',
            help=help,
            description=help,
            epilog=example,
        )
    p.add_argument(
        'source',
        help='path to model metadata files',
    )
    p.add_argument(
        '--prefix',
        default=sys.prefix,
        help='where to install files',
    )
    p.add_argument(
        '--model',
        help='name of the model',
    )

    p.set_defaults(func=execute)

    return p


def execute(args):
    prefix = args.prefix

    model = args.model or ModelMetadata(args.source).api['name']

    # dest = os.path.join(prefix, 'share', 'csdms', args.model)
    dest = os.path.join(prefix, 'share', 'csdms', model)

    # FileSystemLoader(args.source).stage_all(dest)
    env = Environment(loader=FileSystemLoader(args.source))
    with cd(dest):
        for fname in env.list_templates():
            with cd(os.path.dirname(fname) or '.', create=True):
                pass
            shutil.copy2(os.path.join(args.source, fname), fname)


def main():
    import argparse

    p = configure_parser_mmd_install()

    args = p.parse_args()

    args.func(args)
