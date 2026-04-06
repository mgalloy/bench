# encoding: utf-8

"""Module to handle retrieving values from the configuration file. If no value
is found in the configuration file, then a default value is returned.
"""

import configparser
import os
import pathlib


home_dir = pathlib.Path(os.path.expanduser("~"))
configuration_file = home_dir / ".bench"

config = configparser.ConfigParser()
if os.path.exists(configuration_file):
    config.read(configuration_file)


getters = {
    str: config.get,
    int: config.getint,
    float: config.getfloat,
    bool: config.getboolean,
}

# specification for the various options in the configuration file
spec = {
    "plot": {
        "ascii": {"getter_type": bool, "fallback": True},
        "background": {"getter_type": str, "fallback": "light"},
    },
}


def get(section: str, option: str):
    """Get configuration value, falling back to a default if necessary."""
    spec_option = spec[section][option]
    value = getters[spec_option["getter_type"]](
        section, option, fallback=spec_option["fallback"]
    )
    return value
