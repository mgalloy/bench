# encoding: utf-8

""" A command-line utility to do basic display and analysis of tabular data.
"""

import argparse
import datetime
from io import StringIO
import re
import shutil
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

N_COLUMNS, N_ROWS = shutil.get_terminal_size(fallback=(100, 40))
LIGHT_BKG_COLORS = {"axis_color": "black", "title_color": "red"}
DARK_BKG_COLORS = {"axis_color": "white", "title_color": "yellow"}


def date_formatter(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S") if type(dt) == pd.Timestamp else dt


def find_dates(line: str, sep=r"\s+"):
    tokens = re.split(sep, line)
    date_columns = []
    date_formats = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f",
                    "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"]
    for i, t in enumerate(tokens):
        for fmt in date_formats:
            try:
                datetime.datetime.strptime(t, fmt)
                date_columns.append(i)
                break
            except ValueError:
                pass
    return date_columns


def read_data(args):
    """Read data from stdin or from a filename passed as the first argument."""
    format = args.format.lower()
    if format == "csv":
        df, date_indices = read_csv_data(args)
    elif format == "tsv":
        pass
    elif format == "spaces":
        df, date_indices = read_spaces_data(args)
    return df, date_indices


def read_csv_data(args):
    """Read CSV data from stdin or from a filename pass as the
    first argument.
    """
    if sys.stdin.isatty():
        filename = args.PARAMS[0]
        with open(filename) as f:
            for i in range(args.skip_rows):
                f.readline()
            date_indices = find_dates(f.readline(), sep=r"\s*,\s*")
        df = pd.read_csv(
            filename,
            header=None,
            parse_dates=date_indices,
            skiprows=args.skip_rows,
            low_memory=False,
        )
    else:
        args.PARAMS.extend(sys.stdin.read().splitlines())
        date_indices = find_dates(args.PARAMS[args.skip_rows], sep=r"\s*,\s*")
        data = "\n".join(args.PARAMS[args.skip_rows:])
        df = pd.read_csv(
            StringIO(data),
            header=None,
            parse_dates=date_indices,
            low_memory=False,
        )
    return df, date_indices


def read_spaces_data_file(data: str|StringIO, date_indices: list, skip_rows: int|None=None):
    df = pd.read_table(
        data,
        sep=r"\s+",
        header=None,
        parse_dates=date_indices,
        skiprows=skip_rows,
    )

    return df


def read_spaces_data(args):
    """Read data delimited by spaces from stdin or from a filename pass as the
    first argument.
    """
    if sys.stdin.isatty():
        filename = args.PARAMS[0]
        with open(filename) as f:
            for i in range(args.skip_rows):
                f.readline()
            date_indices = find_dates(f.readline())
        df = read_spaces_data_file(filename, date_indices, args.skip_rows)
    else:
        args.PARAMS.extend(sys.stdin.read().splitlines())
        date_indices = find_dates(args.PARAMS[args.skip_rows])
        data = "\n".join(args.PARAMS[args.skip_rows:])
        df = read_spaces_data_file(StringIO(data), date_indices)

    return df, date_indices


def display_table(df, column_indices:list[int]=None, date_indices:list[int]=None):
    formatters = list(date_formatter if i in date_indices else None for i in range(df.shape[1]))
    if column_indices is None:
        indexed_df = df
        indexed_formatters = formatters
    else:
        indexed_df = df.iloc[:, column_indices]
        indexed_formatters = [formatters[i] for i in column_indices]

    try:
        print(indexed_df.to_string(header=False, index=False, formatters=indexed_formatters))
    except BrokenPipeError:
        pass


def parse_column_indices(df, column_expr):
    column_indices = []
    tokens = column_expr.split(",")
    for t in tokens:
        if t.count(":") == 0:
            column_indices.append(int(t))
        elif t.count(":") == 1:
            start, end = (int(sub_t) for sub_t in t.split(":"))
            column_indices.extend(list(range(start, end)))
        else:
            pass   # error
    return column_indices


def filter(args):
    df, date_indices = read_data(args)
    column_indices = args.columns
    if column_indices is not None:
        column_indices = parse_column_indices(df, column_indices)
    display_table(df, column_indices=column_indices, date_indices=date_indices)


def join(args):
    with open(args.left_file) as f:
        # for i in range(args.skip_rows):
        #     f.readline()
        left_date_indices = find_dates(f.readline())
    with open(args.right_file) as f:
        # for i in range(args.skip_rows):
        #     f.readline()
        right_date_indices = find_dates(f.readline())
    left_df = read_spaces_data_file(args.left_file, date_indices=left_date_indices)
    right_df = read_spaces_data_file(args.right_file, date_indices=right_date_indices)

    left_index, right_index = (int(t) for t in args.on.split(":"))
    if args.left:
        how = "left"
    elif args.right:
        how = "right"
    elif args.inner:
        how = "inner"
    elif args.cross:
        how = "cross"
    elif args.left_anti:
        how = "left_anti"
    elif args.right_anti:
        how = "right_anti"
    else:
        how = "inner"
    joined_df = left_df.merge(
        right_df,
        left_on=left_df.columns[left_index],
        right_on=right_df.columns[right_index],
        # how{‘left’, ‘right’, ‘outer’, ‘inner’, ‘cross’, ‘left_anti’, ‘right_anti'}
        how=how,
    )

    date_indices = []
    for di in left_date_indices:
        date_indices.append(di)
    for di in right_date_indices:
        if di == right_index:
            continue
        date_indices.append(di + left_df.shape[1] - (1 if di > right_index else 0))

    display_table(joined_df, date_indices=date_indices)


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
    df, date_indices = read_data(args)

    if args.ascii:
        matplotlib.use("module://mpl_ascii")
    else:
        matplotlib.use("module://itermplot")

    if args.y is None:
        args.parser.error("no y-axis variable specified")
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

    # add filter sub-command
    filter_parser = subparsers.add_parser(
        "filter",
        help="filter rows/columns of table",
    )
    filter_parser.add_argument(
        "--columns",
        type=str,
        metavar="COLUMNS_EXPRESSION",
        help="columns to display",
        default=None,
    )
    filter_parser.add_argument(
        "--skip-rows",
        type=int,
        metavar="N",
        help="number of rows to skip at the beginning of the input",
        default=0,
    )
    filter_parser.add_argument(
        "--format",
        type=str,
        metavar="FORMAT",
        help="format of input data: csv, tsv, or spaces",
        default="spaces",
    )
    filter_parser.add_argument(
        "PARAMS",
        nargs="*",
        help="stdin or filename containing table data",
    )
    filter_parser.set_defaults(func=filter, parser=filter_parser)

    # add join
    join_parser = subparsers.add_parser(
        "join",
        help="join two tables on a common column",
    )
    join_parser.add_argument(
        "--on",
        type=str,
        metavar="INDEX",
        help="""column indices of columns to join on, separated by a colon,
e.g., 0:1 to join on column 0 of the left and column 1 on the right""",
        default="0:0",
    )
    # how{‘left’, ‘right’, ‘outer’, ‘inner’, ‘cross’, ‘left_anti’, ‘right_anti'}
    join_parser.add_argument(
        "--left", action="store_true", help="set to perform a left join"
    )
    join_parser.add_argument(
        "--right", action="store_true", help="set to perform a right join"
    )
    join_parser.add_argument(
        "--outer", action="store_true", help="set to perform a outer join"
    )
    join_parser.add_argument(
        "--inner", action="store_true", help="set to perform a inner join"
    )
    join_parser.add_argument(
        "--cross", action="store_true", help="set to perform a cross join"
    )
    join_parser.add_argument(
        "--left-anti", action="store_true", help="set to perform a left anti join"
    )
    join_parser.add_argument(
        "--right-anti", action="store_true", help="set to perform a right anti join"
    )
    join_parser.add_argument(
        "left_file",
        type=str,
        metavar="LEFT_FILENAME",
        help="first file to join"
    )
    join_parser.add_argument(
        "right_file",
        type=str,
        metavar="RIGHT_FILENAME",
        help="second file to join"
    )
    join_parser.set_defaults(func=join, parser=join_parser)

    # add plot sub-command
    plot_parser = subparsers.add_parser(
        "plot", help="plot two columns against each other",
    )
    plot_parser.add_argument(
        "--dark-background", action="store_true", help="set colors for dark background"
    )
    plot_parser.add_argument("--ascii", action="store_true", help="use ASCII graphics")
    plot_parser.add_argument(
        "--skip-rows",
        type=int,
        metavar="N",
        help="number of rows to skip at the beginning of the input",
        default=0,
    )
    plot_parser.add_argument(
        "--format",
        type=str,
        metavar="FORMAT",
        help="format of input data: csv, tsv, or spaces",
        default="spaces",
    )
    plot_parser.add_argument(
        "-x",
        type=str,
        metavar="INDEX",
        help="column index to use for x-axis variable",
        default=None,
    )
    plot_parser.add_argument(
        "-y",
        type=str,
        metavar="INDEX",
        help="column index to use for y-axis variable",
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
    plot_parser.add_argument(
        "PARAMS",
        nargs="*",
        help="stdin or filename containing table data",
    )
    plot_parser.set_defaults(func=plot, parser=plot_parser)

    args = parser.parse_args()

    # parse args and call appropriate sub-command
    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
