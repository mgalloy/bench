# encoding: utf-8

""" A command-line utility to do basic display and analysis of tabular data.
"""

import argparse
import shutil
import sys

from . import __version__

from . import config
from . import dates
from . import display
from . import readers

# define sub-commands
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

    subcommands = [filter, join, plot, config]
    subcommand_names = "|".join(s.__name__.split(".")[-1] for s in subcommands)

    ascii = "ASCII" if config.get("plot", "ascii") else "iTerm"
    description = f"{name} [columns: {N_COLUMNS}, default graphics: {ascii}]"

    epilog = f"Do '{script_name} ({subcommand_names}) --help' to obtain more help about that sub-command"

    if sys.version_info < (
        3,
        14,
    ):
        parser = argparse.ArgumentParser(description=description, epilog=epilog)
    else:
        parser = argparse.ArgumentParser(
            description=description, epilog=epilog, suggest_on_error=True
        )

    # top-level arguments
    parser.add_argument("-v", "--version", action="version", version=name)

    # show help if no sub-command given
    parser.set_defaults(func=print_help, parser=parser)

    subparsers = parser.add_subparsers(metavar="command")

    # setup sub-commands
    for s in subcommands:
        s.add_arguments(subparsers)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
