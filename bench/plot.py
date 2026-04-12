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


def get_figsize(timeseries: True, width: float|None=None, height: float|None=None):
    """Get size of plot.

    [TODO]: need to convert this with a more accurate method, also depends on
    whether using ASCII or iTerm graphics
    """
    if timeseries:
        default_width = cli.N_COLUMNS / 15
        default_height = 3.75
        if width is not None and height is not None:
            figsize = (width, height)
        elif width is not None:
            figsize = (width, default_height)
        elif height is not None:
            figsize = (default_width, height)
        else:
            figsize = (default_width, default_height)
    else:
        if width is not None and height is not None:
            figsize = (width, height)
        elif width is not None:
            figsize = (width, width)
        elif height is not None:
            figsize = (height, height)
        else:
            default_width = cli.N_COLUMNS / 15
            figsize = (default_width, default_width)
    return figsize


def plot_data(
    x,
    y,
    *,
    xtitle="x-axis",
    ytitle="y-axis",
    title="Plot title",
    xmin:float|None=None,
    xmax:float|None=None,
    ymin:float|None=None,
    ymax:float|None=None,
    width: float|None=None,
    height: float|None=None,
    colors:dict=DARK_BKG_COLORS,
):
    """Plot data as a scatter plot or a time-series (if `x` is an array of
    datetime).
    """

    timeseries = type(x.dtype) is np.dtypes.DateTime64DType
    plt.figure(figsize=get_figsize(timeseries, width, height))

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
    """Plot sub-command handler.
    """
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
        width=args.width,
        height=args.height,
        colors=colors,
    )


def add_arguments(subparsers):
    """Add the "plot" sub-command arguments."""
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
        "--in-format",
        type=str,
        metavar="FORMAT",
        help="format of input data: csv, tsv, or columns",
        default="columns",
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
        "--width",
        type=float,
        help="width of plot",
        default=None,
    )
    plot_parser.add_argument(
        "--height",
        type=float,
        help="height of plot",
        default=None,
    )

    plot_parser.add_argument(
        "PARAMS",
        nargs="*",
        help="stdin or filename containing table data",
    )

    plot_parser.set_defaults(func=plot, parser=plot_parser)
