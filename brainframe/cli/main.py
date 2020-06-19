from argparse import ArgumentParser
import sys
from pathlib import Path
import os
import signal

import i18n

from brainframe.cli import (
    print_utils,
    docker_compose,
    commands,
    defaults,
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

    # Set environment variables to their default values if unset
    if env_vars.INSTALL_PATH not in os.environ:
        os.environ[env_vars.INSTALL_PATH] = str(defaults.INSTALL_PATH)
    # This environment variable must be set as it is used by the
    # docker-compose.yml to find the data path to volume mount
    if env_vars.DATA_PATH not in os.environ:
        os.environ[env_vars.DATA_PATH] = str(defaults.DATA_PATH)

    install_path = Path(os.environ[env_vars.INSTALL_PATH])
    data_path = Path(os.environ[env_vars.DATA_PATH])

    args = parser.parse_args(sys.argv[1:2])

    # Exit with a clean error when interrupted
    def on_sigint(_sig, _frame):
        print("")
        print_utils.fail_translate("portal.interrupted")

    signal.signal(signal.SIGINT, on_sigint)

    if args.command is None:
        print_utils.translate("portal.no-command-provided")
    elif args.command == "install":
        commands.install()
    elif args.command == "backup":
        commands.backup(install_path, data_path)
    elif args.command == "update":
        commands.update(install_path)
    elif args.command == "compose":
        docker_compose.assert_installed(install_path)
        os.chdir(data_path)
        docker_compose.run(install_path, sys.argv[2:])
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
