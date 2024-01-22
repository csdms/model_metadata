#! /usr/bin/env python
from __future__ import print_function

import argparse
import importlib
import sys
import textwrap

from ..api import query
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


def load_component(entry_point):
    module_name, cls_name = entry_point.split(":")

    component = None
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        raise
    else:
        try:
            component = module.__dict__[cls_name]
        except KeyError:
            raise ImportError(cls_name)

    return component


def execute(args):
    model = load_component(args.model)

    for var in args.var:
        try:
            value = query(model, var)
        except MissingSectionError as err:
            print("{0}: Missing section".format(err.name), file=sys.stderr)
        except MissingValueError as err:
            print("{0}: Missing value".format(err.name), file=sys.stderr)
        else:
            print(value, file=sys.stdout)


def main():
    p = configure_parser_mmd_query()

    args = p.parse_args()

    args.func(args)
