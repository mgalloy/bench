# encoding: utf-8

"""Module to handle retrieving values from the configuration file. If no value
is found in the configuration file, then a default value is returned.
"""

import configparser
import os
import pathlib

from . import __version__


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
        "ascii": {
            "getter_type": bool,
            "fallback": True,
            "help": "set to use ASCII graphics",
        },
        "background": {
            "getter_type": str,
            "fallback": "light",
            "help": "default background colorlight or dark",
        },
    },
    "plot2": {
        "ascii": {
            "getter_type": bool,
            "fallback": True,
            "help": "set to use ASCII graphics",
        },
        "background": {
            "getter_type": str,
            "fallback": "light",
            "help": "default background colorlight or dark",
        },
    },
}


def get(section: str, option: str):
    """Get configuration value, falling back to a default if necessary."""
    spec_option = spec[section][option]
    value = getters[spec_option["getter_type"]](
        section, option, fallback=spec_option["fallback"]
    )
    return value


def display_default_config():
    print(f"# Default configuration for table {__version__}\n")

    output = []
    for section_name in spec:
        output.append(f"[{section_name}]")
        max_length = max([len(o) for o in spec[section_name]])
        for option_name, option_specs in spec[section_name].items():
            help = option_specs["help"]
            output.append(f"# {help}")
            default = option_specs["fallback"]
            output.append(f"{option_name:{max_length}} : {default}")
            output.append("")
    else:
        output = output[0:-1]

    print("\n".join(output))
