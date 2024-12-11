from argparse import ArgumentParser

import i18n
from brainframe.cli import brainframe_compose
from brainframe.cli import config
from brainframe.cli import print_utils
from packaging import version

from .utils import command
from .utils import subcommand_parse_args


@command("update")
def update():
    args = _parse_args()

    install_path = config.install_path.value

    brainframe_compose.assert_installed(install_path)

    if args.version == "latest":
        requested_version_str = brainframe_compose.get_latest_version()
    else:
        requested_version_str = args.version

    existing_version_str = brainframe_compose.check_existing_version(
        install_path
    )

    existing_version = version.parse(existing_version_str)
    requested_version = version.parse(requested_version_str)

    force_downgrade = False
    if args.noninteractive:
        # Use the --force flag to decide if downgrades are allowed
        force_downgrade = args.force
    else:
        # Ask the user if downgrades should be allowed
        if existing_version >= requested_version:
            force_downgrade = print_utils.ask_yes_no(
                "update.ask-force-downgrade"
            )

    if not force_downgrade:
        # Fail if the requested version is not an upgrade
        if existing_version == requested_version:
            print_utils.fail_translate(
                "update.version-already-installed",
                existing_version=existing_version_str,
                requested_version=requested_version_str,
            )
        elif existing_version > requested_version:
            print_utils.fail_translate(
                "update.downgrade-not-allowed",
                existing_version=existing_version_str,
                requested_version=requested_version_str,
            )

    print_utils.translate(
        "update.upgrade-version",
        existing_version=existing_version_str,
        requested_version=requested_version_str,
    )

    print_utils.translate("general.downloading-docker-compose")
    docker_compose_path = install_path / "docker-compose.yml"
    brainframe_compose.download(
        docker_compose_path, version=requested_version_str
    )

    brainframe_compose.run(install_path, ["pull"])

    if args.noninteractive:
        restart = args.restart
    else:
        restart = print_utils.ask_yes_no("update.ask-restart")
    if restart:
        brainframe_compose.run(install_path, ["down"])
        brainframe_compose.run(install_path, ["up", "-d"])

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

    parser.add_argument(
        "--force",
        action="store_true",
        help=i18n.t("update.force-help"),
    )

    return subcommand_parse_args(parser)
