import functools
import sys
from argparse import ArgumentParser
from typing import Any
from typing import Callable

from brainframe.cli import os_utils
from brainframe.cli import print_utils

by_name = {}
"""A dict that maps command names to their corresponding function"""


def command(name):
    """A decorator that associates command functions to their command name."""

    def wrapper(function):
        by_name[name] = function

    return wrapper


def subcommand_parse_args(parser: ArgumentParser):
    arg_list = sys.argv[2:]
    args = parser.parse_args(arg_list)

    # Run in non-interactive mode if any flags were provided
    if len(arg_list) > 0:
        args.noninteractive = True

    return args


def requires_root(function: Callable) -> Callable:
    """A decorator that checks if the user is root before running a function"""

    @functools.wraps(function)
    def wrapper(*args, **kwargs) -> Any:
        if not os_utils.is_root():
            print_utils.fail_translate("general.user-not-root")

        return function(*args, **kwargs)

    return wrapper
