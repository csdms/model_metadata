#! /usr/bin/env python
from __future__ import print_function

import sys
import argparse

from ..metadata import find_model_data_files
from ..model_setup import FileSystemLoader


def main():
    """Find model data files."""
    parser = argparse.ArgumentParser(description='Find model data files')
    parser.add_argument('path', type=str, help='path to model metadata')

    args = parser.parse_args()

    sources = FileSystemLoader(args.path).sources
    for path in sources:
        print(path)

    # paths = find_model_data_files(args.path)
    # for path in paths:
    #     print(path)


if __name__ == '__main__':
    sys.exit(main())
