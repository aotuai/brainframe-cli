import getpass
import os
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import List

import i18n

from brainframe.cli import brainframe_compose, dependencies, frozen_utils

from . import config, os_utils, print_utils
from .brainframe_compose import assert_has_docker_permissions

install_path = Path("/usr/local/share/brainframe-kits")
data_path = Path("/var/local/brainframe-kits")


def install(commands: List[str]):
    args = _parse_args()
    print(args)

    # Check all dependencies
    dependencies.docker.ensure(args.noninteractive, args.install_docker)
    # We only require the Docker Compose command in frozen distributions
    if frozen_utils.is_frozen() and shutil.which("docker-compose") is None:
        print_utils.fail_translate(
            "install.install-dependency-manually",
            dependency="docker-compose",
        )

    if not os_utils.added_to_group("docker"):
        if args.noninteractive:
            add_to_group = args.add_to_docker_group
        else:
            add_to_group = print_utils.ask_yes_no("install.ask-add-to-docker-group")

        if add_to_group:
            os_utils.add_to_group("docker")

    install_path.mkdir(parents=True, exist_ok=True)
    data_path.mkdir(parents=True, exist_ok=True)

    # Set up permissions with the 'brainframe' group
    print_utils.translate("install.create-group-justification")
    os_utils.create_group("brainframe", os_utils.BRAINFRAME_GROUP_ID)
    os_utils.give_brainframe_group_rw_access([data_path, install_path])

    # Optionally add the user to the "brainframe" group
    if not os_utils.added_to_group("brainframe"):
        if args.noninteractive:
            add_to_group = args.add_to_group
        else:
            add_to_group = print_utils.ask_yes_no("install.ask-add-to-group")

        if add_to_group:
            os_utils.add_to_group("brainframe")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    docker_compose_mgmt = os.path.join(script_dir, "docker-compose-kits.yml")
    install_file = install_path.joinpath("docker-compose.yml")
    shutil.copy(docker_compose_mgmt, install_file)

    print_utils.translate("install.downloading-images")
    brainframe_compose.run(install_path, ["pull"])

    print(f"The BrainFrame Kits was installed:")
    print(f"\t\t\t\t1) deployment path: {install_path}")
    print(f"\t\t\t\t2) data path: {data_path}")

    print_utils.translate("kits.description")
    print_utils.translate("kits.usage")


def start(commands: List[str]):
    brainframe_compose.run(install_path, commands)


def stop(commands: List[str]):
    brainframe_compose.run(install_path, ["up", "-d"])


def run(commands: List[str]) -> None:
    assert_has_docker_permissions()

    if "install" in commands:
        install(commands)
    else:
        assert_has_docker_permissions()
        brainframe_compose.run(install_path, commands)


def _parse_args():
    parser = ArgumentParser(
        description=i18n.t("kits.description"),
        usage=i18n.t("kits.usage"),
    )

    parser.add_argument(
        "--noninteractive",
        action="store_true",
        help=i18n.t("general.noninteractive-help"),
    )
    parser.add_argument(
        "--install-docker",
        action="store_true",
        help=i18n.t("install.install-docker-help"),
    )
    parser.add_argument(
        "--add-to-group",
        action="store_true",
        help=i18n.t("install.add-to-group-help"),
    )
    parser.add_argument(
        "--add-to-docker-group",
        action="store_true",
        help=i18n.t("install.add-to-docker-group-help"),
    )
    parser.add_argument(
        "--version",
        type=str,
        default="latest",
        help=i18n.t("install.version-help"),
    )

    arg_list = sys.argv[3:]
    args = parser.parse_args(arg_list)

    # Run in non-interactive mode if any flags were provided
    if len(arg_list) > 0:
        args.noninteractive = True

    return args
