# encoding: utf-8

""" A command-line utility to do basic display and analysis of tabular data.
"""

import argparse
import shutil

from . import __version__

from . import config
from . import dates
from . import display
from . import readers

from . import filter
from . import join
from . import plot


try:
    import pandas as pd

    PANDAS_REQUIREMENTS = True
except:
    PANDAS_REQUIREMENTS = False


N_COLUMNS, N_ROWS = shutil.get_terminal_size(fallback=(100, 40))


def print_help(args):
    args.parser.print_help()


def main():
    script_name = "table"
    name = f"{script_name} {__version__}"

    description = f"{name} [columns: {N_COLUMNS}]"

    parser = argparse.ArgumentParser(description=description)

    # top-level arguments
    parser.add_argument("-v", "--version", action="version", version=name)

    # show help if no sub-command given
    parser.set_defaults(func=print_help, parser=parser)

    subparsers = parser.add_subparsers(metavar="command")

    # setup sub-commands
    filter.add_arguments(subparsers)
    join.add_arguments(subparsers)
    plot.add_arguments(subparsers)

    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
