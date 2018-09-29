import argparse
import textwrap

from .. import __version__
from .main_dump import configure_parser_mmd_dump
from .main_find import configure_parser_mmd_find
from .main_install import configure_parser_mmd_install
from .main_stage import configure_parser_mmd_stage


def configure_parser_mmd(sub_parsers=None):
    help = "Model metadata tools"

    example = textwrap.dedent(
        """

    Examples:

    mmd --version

    """
    )
    if sub_parsers is None:
        p = argparse.ArgumentParser(
            description=help, fromfile_prefix_chars="@", epilog=example
        )
    else:
        p = sub_parsers.add_parser("mmd", help=help, description=help, epilog=example)
    # p.add_argument(
    #     'name',
    #     help='name of model',
    # )

    p.add_argument(
        "-V",
        "--version",
        action="version",
        version="mmd {0}".format(__version__),
        help="Show the mmd version number and exit.",
    )

    sub_parsers = p.add_subparsers(metavar="command", dest="cmd")
    sub_parsers.required = True
    # p.set_defaults(func=execute)

    configure_parser_mmd_find(sub_parsers)
    configure_parser_mmd_stage(sub_parsers)
    configure_parser_mmd_dump(sub_parsers)
    configure_parser_mmd_install(sub_parsers)

    return p


def main():
    p = configure_parser_mmd()
    args = p.parse_args()

    args.func(args)
