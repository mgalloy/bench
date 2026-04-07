# encoding: utf-8

"""Plot sub-command.
"""

try:
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt

    PLOT_REQUIREMENTS = True
except:
    PLOT_REQUIREMENTS = False

from . import cli
from . import config
from . import readers


LIGHT_BKG_COLORS = {"axis_color": "black", "title_color": "red"}
DARK_BKG_COLORS = {"axis_color": "white", "title_color": "yellow"}
BKG_COLORS = {"dark": DARK_BKG_COLORS, "light": LIGHT_BKG_COLORS}


def plot_data(
    x,
    y,
    *,
    xtitle="x-axis",
    ytitle="y-axis",
    title="Plot title",
    xmin=None,
    xmax=None,
    ymin=None,
    ymax=None,
    colors=DARK_BKG_COLORS,
):
    """Plot data as a scatter plot or a time-series (if `x` is an array of
    datetime).
    """

    timeseries = type(x.dtype) is np.dtypes.DateTime64DType

    # [TODO]: need to convert this with a more accurate method, also depends on
    # whether using ASCII or iTerm graphics; also maybe on time series vs 2
    # non-time variables
    if timeseries:
        width = cli.N_COLUMNS / 8
        figsize = (width, 3.75)
    else:
        width = cli.N_COLUMNS / 15
        figsize = (width, width)

    plt.figure(figsize=figsize)

    ax = plt.subplot(111)
    ax.spines[["top", "right", "bottom", "left"]].set_color(colors["axis_color"])
    ax.spines[["top", "right"]].set_visible(False)

    ax.scatter(x, y, color="r", s=2.0, marker="o")

    if xmin is not None or xmax is not None:
        ax.set_xlim(xmin, xmax)
    if ymin is not None or ymax is not None:
        ax.set_ylim(ymin, ymax)

    ax.set_xlabel(xtitle, color=colors["title_color"])
    ax.set_ylabel(ytitle, color=colors["title_color"])
    ax.set_title(title, color=colors["title_color"])

    ax.tick_params(axis="x", colors=colors["axis_color"])
    ax.tick_params(axis="y", colors=colors["axis_color"])

    plt.show()


def plot(args):
    df, date_indices = readers.read_data(args)

    use_ascii = args.ascii
    if use_ascii is None:
        use_ascii = config.get("plot", "ascii")

    if use_ascii:
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

    if args.dark_background:
        colors = DARK_BKG_COLORS
    elif args.light_background:
        colors = LIGHT_BKG_COLORS
    else:
        colors = BKG_COLORS[config.get("plot", "background")]

    plot_data(
        x,
        y,
        xtitle=xtitle,
        ytitle=ytitle,
        title=title,
        xmin=args.xmin,
        xmax=args.xmax,
        ymin=args.ymin,
        ymax=args.ymax,
        colors=colors,
    )


def add_arguments(subparsers):
    """Add the "plot" sub-command.
    """
    plot_parser = subparsers.add_parser(
        "plot",
        help="plot two columns against each other",
    )

    plot_parser.add_argument(
        "--dark-background",
        action="store_true",
        help="set colors for dark background",
        default=None,
    )
    plot_parser.add_argument(
        "--light-background",
        action="store_true",
        help="set colors for light background",
        default=None,
    )

    plot_parser.add_argument(
        "--ascii", action="store_true", help="use ASCII graphics", default=None
    )

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
        "--xmin",
        type=float,
        help="minimum value for x-axis range",
        default=None,
    )
    plot_parser.add_argument(
        "--xmax",
        type=float,
        help="maximum value for x-axis range",
        default=None,
    )
    plot_parser.add_argument(
        "--ymin",
        type=float,
        help="minimum value for y-axis range",
        default=None,
    )
    plot_parser.add_argument(
        "--ymax",
        type=float,
        help="maximum value for y-axis range",
        default=None,
    )

    plot_parser.add_argument(
        "PARAMS",
        nargs="*",
        help="stdin or filename containing table data",
    )

    plot_parser.set_defaults(func=plot, parser=plot_parser)
