#! /usr/bin/env python
from __future__ import print_function

import sys
import argparse

from ..model_metadata import ModelMetadata


def main():
    parser = argparse.ArgumentParser(description='Get info about a model')
    parser.add_argument('path', type=str, help='path to model metadata')
    parser.add_argument('--section', action='append', type=str,
                        help='name of metadata section')

    args = parser.parse_args()

    if args.section:
        for name in args.section:
            print(ModelMetadata(args.path).dump_section(name))
    else:
        print(ModelMetadata(args.path).dump())


if __name__ == '__main__':
    sys.exit(main())
