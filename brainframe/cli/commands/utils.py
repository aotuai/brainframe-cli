from argparse import ArgumentParser
import sys
from abc import ABC


def subcommand_parse_args(parser: ArgumentParser):
    arg_list = sys.argv[2:]
    args = parser.parse_args(arg_list)

    # Run in non-interactive mode if any flags were provided
    if len(arg_list) > 0:
        args.noninteractive = True

    return args
