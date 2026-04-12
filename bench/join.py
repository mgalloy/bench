# encoding: utf-8

from . import dates
from . import display
from . import readers


def join_handler(args):
    """Handle join sub-command actions.
    """
    try:
        with open(args.left_file) as f:
            # for i in range(args.skip_rows):
            #     f.readline()
            left_date_indices = dates.find_dates(f.readline())
    except FileNotFoundError:
        args.parser.error(f"file not found {args.left_file}")
    try:
        with open(args.right_file) as f:
            # for i in range(args.skip_rows):
            #     f.readline()
            right_date_indices = dates.find_dates(f.readline())
    except FileNotFoundError:
        args.parser.error(f"file not found {args.right_file}")

    left_df = readers.read_columns_data_file(
        args.left_file, date_indices=left_date_indices
    )
    right_df = readers.read_columns_data_file(
        args.right_file, date_indices=right_date_indices
    )

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

    display.display_table(joined_df, date_indices=date_indices, format=args.out_format)


def add_arguments(subparsers):
    """Add join sub-command arguments.
    """
    join_parser = subparsers.add_parser(
        "join",
        help="join two tables on a common column",
    )
    join_parser.add_argument(
        "--out-format",
        type=str,
        metavar="FORMAT",
        help="format of input data: columns, html, latex, or markdown",
        default="columns",
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
        "left_file", type=str, metavar="LEFT_FILENAME", help="first file to join"
    )
    join_parser.add_argument(
        "right_file", type=str, metavar="RIGHT_FILENAME", help="second file to join"
    )
    join_parser.set_defaults(func=join_handler, parser=join_parser)
