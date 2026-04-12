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
            "help": "default background color: \"light\" or \"dark\"",
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
    print(f"# Default configuration for table {__version__}")
    print(f"# Place in {configuration_file}\n")

    output = []
    max_length = max([len(o) for s in spec for o in spec[s]])
    for section_name in spec:
        output.append(f"[{section_name}]")
        for option_name, option_specs in spec[section_name].items():
            help = option_specs["help"]
            output.append(f"# {help}")
            default = option_specs["fallback"]
            output.append(f"{option_name:{max_length}} : {default}")
            output.append("")
    else:
        output = output[0:-1]

    print("\n".join(output))


def set_option(section: str, option: str, value):
    """Set the option to the given value in the configuration file.
    """
    # [TODO]: need to do this still
    print(f"NOT IMPLEMENTED: setting {section}.{option} = {value}")


def config_handler(args):
    """Handle config sub-command actions.
    """
    if args.defaults:
        display_default_config()
        return

    if args.option is not None:
        try:
            section, option = args.option.split(".")
        except ValueError as e:
            args.parser.error(f"invalid option name: \"{args.option}\", name should be in the format \"section.option\"")
        if args.value is None:
            value = config.get(section, option)
            print(f"{section}.{option} = {value}")
        else:
            set_option(section, option, args.value)


def add_arguments(subparsers):
    """Add the "plot" sub-command arguments."""
    config_parser = subparsers.add_parser(
        "config",
        help="handle configuration",
    )
    config_parser.add_argument(
        "--defaults", action="store_true", help="print default configuration", default=None
    )
    config_parser.add_argument(
        "option", type=str, nargs="?", metavar="OPTION_NAME", help="option name in the format \"section.option\"", default=None
    )
    config_parser.add_argument(
        "value", type=str, nargs="?", metavar="VALUE", help="option value", default=None
    )

    config_parser.set_defaults(func=config_handler, parser=config_parser)
