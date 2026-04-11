# encoding: utf-8

from io import StringIO
import sys

import pandas as pd

from . import dates


def read_data(args):
    """Read data from stdin or from a filename passed as the first argument."""
    format = args.in_format.lower()
    if format == "csv":
        df, date_indices = read_csv_data(args)
    elif format == "tsv":
        pass
    elif format == "columns":
        df, date_indices = read_columns_data(args)
    return df, date_indices


def read_csv_data(args):
    """Read CSV data from stdin or from a filename pass as the
    first argument.
    """
    if sys.stdin.isatty():
        filename = args.PARAMS[0]
        try:
            with open(filename) as f:
                for i in range(args.skip_rows):
                    f.readline()
                date_indices = dates.find_dates(f.readline(), sep=r"\s*,\s*")
        except FileNotFoundError:
            args.parser.error(f"file not found: {filename}")
        df = pd.read_csv(
            filename,
            header=None,
            parse_dates=date_indices,
            skiprows=args.skip_rows,
            low_memory=False,
        )
    else:
        args.PARAMS.extend(sys.stdin.read().splitlines())
        date_indices = dates.find_dates(args.PARAMS[args.skip_rows], sep=r"\s*,\s*")
        data = "\n".join(args.PARAMS[args.skip_rows :])
        df = pd.read_csv(
            StringIO(data),
            header=None,
            parse_dates=date_indices,
            low_memory=False,
        )
    return df, date_indices


def read_columns_data_file(
    data: str | StringIO, date_indices: list, skip_rows: int | None = None
):
    df = pd.read_table(
        data,
        sep=r"\s+",
        header=None,
        parse_dates=date_indices,
        skiprows=skip_rows,
    )

    return df


def read_columns_data(args):
    """Read data delimited by spaces from stdin or from a filename pass as the
    first argument.
    """
    if sys.stdin.isatty():
        filename = args.PARAMS[0]
        try:
            with open(filename) as f:
                for i in range(args.skip_rows):
                    f.readline()
                date_indices = dates.find_dates(f.readline())
        except FileNotFoundError:
            args.parser.error(f"file not found: {filename}")
        df = read_columns_data_file(filename, date_indices, args.skip_rows)
    else:
        args.PARAMS.extend(sys.stdin.read().splitlines())
        date_indices = dates.find_dates(args.PARAMS[args.skip_rows])
        data = "\n".join(args.PARAMS[args.skip_rows :])
        df = read_columns_data_file(StringIO(data), date_indices)

    return df, date_indices
