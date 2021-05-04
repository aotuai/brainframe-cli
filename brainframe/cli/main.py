#!/usr/bin/env python3

import os
import signal
import sys
from argparse import ArgumentParser

import i18n
from brainframe.cli import (
    commands,
    config,
    os_utils,
    print_utils,
    translations,
)


def main():
    i18n.load_path.append(str(translations.PATH))

    parser = ArgumentParser(
        description=i18n.t("portal.description"), usage=i18n.t("portal.usage")
    )

    parser.add_argument(
        "command", default=None, nargs="?", help=i18n.t("portal.command-help")
    )

    config.load()

    # This environment variable must be set as it is used by the
    # docker-compose.yml to find the data path to volume mount
    if config.data_path.name not in os.environ:
        os.environ[config.data_path.name] = str(config.data_path.default)

    args = parser.parse_args(sys.argv[1:2])

    # Exit with a clean error when interrupted
    def on_sigint(_sig, _frame):
        print()
        if os_utils.current_command is not None:
            os_utils.current_command.send_signal(_sig)
        print_utils.fail_translate("portal.interrupted")

    signal.signal(signal.SIGINT, on_sigint)

    if args.command is None:
        print_utils.translate("portal.no-command-provided")
    elif args.command in commands.by_name:
        command = commands.by_name[args.command]
        command()
    else:
        error_message = i18n.t("portal.unknown-command")
        error_message = error_message.format(command=args.command)
        print_utils.print_color(
            error_message, color=print_utils.Color.RED, file=sys.stderr
        )
        parser.print_help()


if __name__ == "__main__":
    main()
