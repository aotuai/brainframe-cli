import os
import signal
import sys
from argparse import ArgumentParser

import i18n

from brainframe.cli import (
    print_utils,
    commands,
    env_vars,
)


def main():
    i18n.load_path.append(_TRANSLATIONS_PATH)

    parser = ArgumentParser(
        description=i18n.t("portal.description"), usage=i18n.t("portal.usage")
    )

    parser.add_argument(
        "command", default=None, nargs="?", help=i18n.t("portal.command-help")
    )

    # This environment variable must be set as it is used by the
    # docker-compose.yml to find the data path to volume mount
    if not env_vars.data_path.is_set():
        os.environ[env_vars.data_path.name] = str(env_vars.data_path.default)

    args = parser.parse_args(sys.argv[1:2])

    # Exit with a clean error when interrupted
    def on_sigint(_sig, _frame):
        print()
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


_TRANSLATIONS_PATH = os.path.join(os.path.dirname(__file__), "translations")

if __name__ == "__main__":
    main()
