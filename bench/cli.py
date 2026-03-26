#!/usr/bin/env python

""" A command-line utility to do basic display and analysis of tabular data.
"""

import argparse
import datetime
from io import StringIO
import os
import sys

try:
    import pandas as pd

    PANDAS_REQUIREMENTS = True
except:
    PANDAS_REQUIREMENTS = False

try:
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt

    PLOT_REQUIREMENTS = True
except:
    PLOT_REQUIREMENTS = False

from . import __version__


N_COLUMNS = os.get_terminal_size().columns
LIGHT_BKG_COLORS = {"axis_color": "black", "title_color": "red"}
DARK_BKG_COLORS = {"axis_color": "white", "title_color": "yellow"}


def find_dates(line: str):
    tokens = line.split()
    date_columns = []
    date_format = "%Y-%m-%dT%H:%M:%S.%f"
    for i, t in enumerate(tokens):
        try:
            datetime.datetime.strptime(t, date_format)
            date_columns.append(i)
        except ValueError:
            pass
    return date_columns


def read_data(args):
    """Read data from stdin or from a filename passed as the first argument."""
    if sys.stdin.isatty():
        filename = args.PARAMS[0]
        with open(filename) as f:
            date_indices = find_dates(f.readline())
        df = pd.read_table(filename, sep=r"\s+", header=None, parse_dates=date_indices)
    else:
        args.PARAMS.extend(sys.stdin.read().splitlines())
        date_indices = find_dates(args.PARAMS[0])
        data = "\n".join(args.PARAMS)
        df = pd.read_table(
            StringIO(data), sep=r"\s+", header=None, parse_dates=date_indices
        )

    return df


def plot_data(
    x=None,
    y=None,
    xtitle="x-axis",
    ytitle="y-axis",
    title="Plot title",
    colors=DARK_BKG_COLORS,
):
    """Plot data."""
    if x is None:
        x = np.arange(0, 10, 0.1)
    if y is None:
        y = np.sin(np.sinc(x))

    plt.figure(figsize=(N_COLUMNS / 10, 4))

    ax = plt.subplot(111)
    ax.spines[["top", "right", "bottom", "left"]].set_color(colors["axis_color"])
    ax.spines[["top", "right"]].set_visible(False)

    ax.scatter(x, y, color="r", s=2.0, marker="o")
    ax.set_xlabel(xtitle, color=colors["title_color"])
    ax.set_ylabel(ytitle, color=colors["title_color"])
    ax.set_title(title, color=colors["title_color"])
    ax.tick_params(axis="x", colors=colors["axis_color"])
    ax.tick_params(axis="y", colors=colors["axis_color"])

    plt.show()


def plot(args):
    df = read_data(args)

    if args.ascii:
        matplotlib.use("module://mpl_ascii")
    else:
        matplotlib.use("module://itermplot")


    if args.y is None:
        pass  # TODO: should fail here
    else:
        yindex = int(args.y)
        if args.x is None:
            xindex = None
        else:
            xindex = int(args.x)

    y = df.iloc[:, yindex].to_numpy()
    ytitle = f"column {yindex}" if args.ytitle is None else args.ytitle

    if xindex is None:
        x = np.arange(0, len(y))
        xtitle = "Row index"
    else:
        x = df.iloc[:, xindex].to_numpy()
        xtitle = f"column {xindex}"

    xtitle = xtitle if args.xtitle is None else args.xtitle

    title = f"{xtitle} vs {ytitle}" if args.title is None else args.title

    # print(repr(args))
    # colors = DARK_BKG_COLORS if args.dark_background else LIGHT_BKG_COLORS
    # example_plot(colors=colors)
    plot_data(x, y, xtitle, ytitle, title)


def print_help(args):
    args.parser.print_help()


def main():
    script_name = "table"
    name = f"{script_name} {__version__}"

    description = f"{script_name} number of columns: {N_COLUMNS}"

    parser = argparse.ArgumentParser(description=description)

    # top-level arguments
    parser.add_argument("-v", "--version", action="version", version=name)

    # show help if no sub-command given
    parser.set_defaults(func=print_help, parser=parser)

    subparsers = parser.add_subparsers(metavar="command")

    plot_parser = subparsers.add_parser(
        "plot", help="plot two columns against each other"
    )
    plot_parser.add_argument(
        "--dark-background", action="store_true", help="set colors for dark background"
    )
    plot_parser.add_argument(
        "--ascii", action="store_true", help="use ASCII graphics"
    )
    plot_parser.add_argument(
        "-x",
        type=str,
        help="column name/index to use for x-axis variable",
        default=None,
    )
    plot_parser.add_argument(
        "-y",
        type=str,
        help="column name/index to use for y-axis variable",
        default=None,
    )
    plot_parser.add_argument(
        "--xtitle",
        type=str,
        help="title for x-axis",
        default=None,
    )
    plot_parser.add_argument(
        "--ytitle",
        type=str,
        help="title for y-axis",
        default=None,
    )
    plot_parser.add_argument(
        "--title",
        type=str,
        help="title for plot",
        default=None,
    )
    # TODO: need some common options for many of the parsers:
    #   --skip_rows N
    #   --type TYPE where TYPE is "csv", "tsv", "spaces"
    plot_parser.set_defaults(func=plot, parser=plot_parser)

    plot_parser.add_argument("PARAMS", nargs="*")

    args = parser.parse_args()

    # parse args and call appropriate sub-command
    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
