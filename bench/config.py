# encoding: utf-8

import configparser
import os
import pathlib


home_dir = pathlib.Path(os.path.expanduser("~"))
configuration_file = home_dir / ".bench"

config = configparser.ConfigParser()
if os.path.exists(configuration_file):
    config.read(configuration_file)


# specification for the various options in the configuration file
spec = {"plot": {"ascii" : {"reader": config.getboolean, "fallback": True},
                 "background" : {"reader": config.get, "fallback": "light"}},}


def get(section: str, option: str):
    """Get configuration value, falling back to a default if necessary.
    """
    spec_option = spec[section][option]
    value = spec_option["reader"](section, option, fallback=spec_option["reader"])
    return value
