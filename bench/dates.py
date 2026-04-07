# encoding: utf-8

import datetime
import re


VALID_DATE_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
]


def find_dates(line: str, sep=r"\s+"):
    """Find the columns in the test line of a file that match one of the
    approved date/time formats.
    """
    tokens = re.split(sep, line)
    date_columns = []

    for i, t in enumerate(tokens):
        for fmt in VALID_DATE_FORMATS:
            try:
                datetime.datetime.strptime(t, fmt)
                date_columns.append(i)
                break
            except ValueError:
                pass
    return date_columns
