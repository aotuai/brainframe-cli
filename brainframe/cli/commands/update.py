from argparse import ArgumentParser

import i18n

from brainframe.cli import print_utils, docker_compose, env_vars
from .utils import subcommand_parse_args, command


@command("update")
def update():
    args = _parse_args()

    install_path = env_vars.install_path.get()

    docker_compose.assert_installed(install_path)

    print_utils.translate("general.downloading-docker-compose")
    docker_compose_path = install_path / "docker-compose.yml"
    docker_compose.download(docker_compose_path, version=args.version)

    docker_compose.run(install_path, ["pull"])

    if args.noninteractive:
        restart = args.restart
    else:
        restart = print_utils.ask_yes_no("update.ask-restart")
    if restart:
        docker_compose.run(install_path, ["down"])
        docker_compose.run(install_path, ["up", "-d"])

    print()
    print_utils.translate("update.complete", color=print_utils.Color.GREEN)


def _parse_args():
    parser = ArgumentParser(
        description=i18n.t("update.description"), usage=i18n.t("update.usage")
    )

    parser.add_argument(
        "--noninteractive",
        action="store_true",
        help=i18n.t("general.noninteractive-help"),
    )

    parser.add_argument(
        "--version",
        type=str,
        default="latest",
        help=i18n.t("update.version-help"),
    )

    parser.add_argument(
        "--restart", action="store_true", help=i18n.t("update.restart-help")
    )

    return subcommand_parse_args(parser)
