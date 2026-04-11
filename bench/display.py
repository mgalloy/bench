# encoding: utf-8

"""Library routines to handle displaying a table.
"""

import pandas as pd


def date_formatter(dt: pd.Timestamp):
    """Format an element that might be a `pd.Timestamp`."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S") if type(dt) == pd.Timestamp else dt


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
        s = indexed_df.to_string(header=False, index=False, formatters=indexed_formatters)
    elif format == "html":
        s = indexed_df.to_html(index=False, formatters=indexed_formatters)
    elif format == "latex":
        s = indexed_df.to_latex(index=False)#, formatters=indexed_formatters)
    elif format == "markdown":
        s = indexed_df.to_markdown(index=False)
    else:
        s = indexed_df.to_string(header=False, index=False, formatters=indexed_formatters)
    try:
        print(s)
    except (BrokenPipeError, KeyboardInterrupt):
        pass
