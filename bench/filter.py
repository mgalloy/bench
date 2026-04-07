# encoding: utf-8

from . import display
from . import readers


def parse_indices(dim_size: int, expr: str):
    indices = []
    tokens = expr.split(",")
    for t in tokens:
        if t.count(":") == 0:
            indices.append(int(t))
        elif t.count(":") == 1:
            start, end = (sub_t for sub_t in t.split(":"))
            start = int(start)
            end = int(end) if end != "" else dim_size
            indices.extend(list(range(start, end)))
        else:
            pass  # error
    return indices


def filter(args):
    df, date_indices = readers.read_data(args)

    columns_expr = args.columns
    if columns_expr is not None:
        column_indices = parse_indices(df.shape[1], columns_expr)
    else:
        column_indices = None

    row_expr = args.rows
    if row_expr is not None:
        row_indices = parse_indices(df.shape[0], row_expr)
    else:
        row_indices = None

    display.display_table(
        df,
        column_indices=column_indices,
        row_indices=row_indices,
        date_indices=date_indices,
    )

def add_arguments(subparsers):
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
        "--rows",
        type=str,
        metavar="ROWS_EXPRESSION",
        help="rows to display (indexing does not include skipped rows)",
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

