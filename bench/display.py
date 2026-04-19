# encoding: utf-8

"""Library routines to handle displaying a table in various formats.
"""

import pandas as pd


def date_formatter(ts: pd.Timestamp):
    """Format an element that might be a `pd.Timestamp`."""
    if type(ts) == pd.Timestamp:
        if ts.microsecond == 0:
            return ts.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            millisecond = f"{ts.microsecond:06}"[0:3]
            return ts.strftime("%Y-%m-%dT%H:%M:%S.{}").format(millisecond)
    else:
        return ts
    # return ts.strftime("%Y-%m-%dT%H:%M:%S.%f") if type(ts) == pd.Timestamp else ts


def display_table(
    df,
    column_indices: list[int] = None,
    row_indices: list[int] = None,
    date_indices: list[int] = None,
    format: str = "columns",
):
    """Print a table."""
    formatters = list(
        date_formatter if i in date_indices else None for i in range(df.shape[1])
    )

    if column_indices is None:
        indexed_df = df
        indexed_formatters = formatters
    else:
        indexed_df = df.iloc[:, column_indices]
        indexed_formatters = [formatters[i] for i in column_indices]

    if row_indices is not None:
        indexed_df = indexed_df.iloc[row_indices, :]

    if format == "columns":
        # [TODO]: use line_width set to terminal width?
        s = indexed_df.to_string(
            header=False, index=False, formatters=indexed_formatters
        )
    elif format == "html":
        s = indexed_df.to_html(index=False, formatters=indexed_formatters)
    elif format == "latex":
        s = indexed_df.to_latex(index=False)  # , formatters=indexed_formatters)
    elif format == "markdown":
        # [TODO]: this does not work well and doesn't respect all the keywords,
        # it might be better to make my own
        # floatfmt = list(
        #     "%Y-%m-%dT%H:%M:%S" if i in date_indices else "" for i in range(df.shape[1])
        # )
        # if column_indices is not None:
        #     floatfmt = [floatfmt[i] for i in column_indices]
        s = indexed_df.to_markdown(
            index=False,
            # floatfmt=floatfmt,
        )
    else:
        s = indexed_df.to_string(
            header=False, index=False, formatters=indexed_formatters
        )
    try:
        print(s)
    except (BrokenPipeError, KeyboardInterrupt):
        pass
