#!/usr/bin/env python3

import os
import signal
import sys
from argparse import ArgumentParser

import i18n
from brainframe.cli import __version__
from brainframe.cli import commands
from brainframe.cli import config
from brainframe.cli import frozen_utils
from brainframe.cli import os_utils
from brainframe.cli import print_utils


def main():
    i18n.load_path.append(str(frozen_utils.TRANSLATIONS_PATH))

    parser = ArgumentParser(
        description=i18n.t("portal.description"), usage=i18n.t("portal.usage")
    )

    parser.add_argument(
        "command", default=None, nargs="?", help=i18n.t("portal.command-help")
    )
    parser.add_argument(
        "--version",
        action="version",
        version="brainframe {}".format(__version__),
    )

    config.load()

    # This environment variable must be set as it is used by the
    # docker-compose.yml to find the data path to volume mount
    os.environ.setdefault(
        config.data_path.env_var_name,
        str(config.data_path.default),
    )

    args = parser.parse_args(sys.argv[1:2])

    # Exit with a clean error when interrupted
    def on_sigint(sig, _frame):
        print()
        if os_utils.current_command.process is None:
            print_utils.fail_translate("general.interrupted")
        else:
            # Let os_utils.run take care of bringing the process down when the current
            # command is finished
            os_utils.current_command.send_signal(sig)

    signal.signal(signal.SIGINT, on_sigint)

    if args.command is None:
        print_utils.translate("portal.no-command-provided")
        sys.exit(2)
    elif args.command in commands.by_name:
        command = commands.by_name[args.command]
        command()
    else:
        error_message = i18n.t("portal.unknown-command")
        error_message = error_message.format(command=args.command)
        parser.error(error_message)


if __name__ == "__main__":
    main()
