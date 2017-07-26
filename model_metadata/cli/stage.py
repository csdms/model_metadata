#! /usr/bin/env python
from __future__ import print_function

import sys
import argparse

from ..model_setup import FileSystemLoader


def main():
    """Find model data files."""
    parser = argparse.ArgumentParser(description='Stage model data files')
    parser.add_argument('path', type=str, help='path to model metadata')
    parser.add_argument('dest', type=str, help='stage folder')

    args = parser.parse_args()

    # stage_model_run(args.path, args.dest)

    FileSystemLoader(args.path).stage_all(args.dest)


if __name__ == '__main__':
    sys.exit(main())
