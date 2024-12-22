import os
import subprocess
import sys
from pathlib import Path
from typing import List
from typing import Optional
from typing import Tuple

import i18n
import requests
import yaml

from . import config
from . import frozen_utils
from . import os_utils
from . import print_utils

# The URL to the docker-compose.yml
BRAINFRAME_DOCKER_COMPOSE_URL = "https://{subdomain}aotu.ai/releases/brainframe/{version}/docker-compose.yml"
# The URL to the latest tag, which is just a file containing the latest version
# as a string
BRAINFRAME_LATEST_TAG_URL = (
    "https://{subdomain}aotu.ai/releases/brainframe/latest"
)


def assert_installed(install_path: Path) -> None:
    compose_path = install_path / "docker-compose.yml"

    if not compose_path.is_file():
        print_utils.fail_translate(
            "general.brainframe-must-be-installed",
            install_env_var=config.install_path.name,
        )


def get_docker_compose_command():
    try:
        # First, try to use 'docker compose'
        compose_version = subprocess.check_output(
            ["docker", "compose", "version", "--short"],
            stderr=subprocess.DEVNULL,
        )
        return ["docker", "compose"], compose_version
    except subprocess.CalledProcessError as e2:
        try:
            compose_version = subprocess.check_output(
                ["docker-compose", "version", "--short"],
                stderr=subprocess.DEVNULL,
            )
            return ["docker-compose"], compose_version
        except subprocess.CalledProcessError as e1:
            message = f"Docker Compose V1: {e}; V2: {e}"
            raise DockerComposeNotFoundError(message)


def run(install_path: Path, commands: List[str]) -> None:
    assert_has_docker_permissions()

    compose_path = install_path / "docker-compose.yml"

    full_command, _ = get_docker_compose_command()

    full_command += [
        "--file",
        str(compose_path),
    ]

    # Provide the override file if it exists
    compose_override_path = install_path / "docker-compose.override.yml"
    if compose_override_path.is_file():
        full_command += ["--file", str(compose_override_path)]

    # Provide the .env file if it exists
    env_path = install_path / ".env"
    if env_path.is_file():
        full_command += ["--env-file", str(env_path)]

    additional_help = None
    if "down" in commands:
        if "--except-volumes" in commands:
            commands.remove("--except-volumes")
        else:
            if "--volumes" not in commands:
                commands += ["--volumes"]
        if "--help" in commands:
            additional_help = '    --except-volumes        Do not add --volumes to "brainframe compose down"'

    os_utils.run(full_command + commands)

    if additional_help is not None:
        print_utils.print_color(
            additional_help, color=print_utils.Color.MAGENTA, file=sys.stderr
        )


def download(target: Path, version: str = "latest") -> None:
    _assert_has_write_permissions(target.parent)

    if version == "latest":
        version = get_latest_version()

    credentials = config.staging_credentials()

    url = BRAINFRAME_DOCKER_COMPOSE_URL.format(
        subdomain="staging." if config.is_staging.value else "",
        version=version,
    )
    response = requests.get(url, auth=credentials, stream=True)
    if not response.ok:
        print_utils.fail_translate(
            "general.error-downloading-docker-compose",
            status_code=response.status_code,
            error_message=response.text,
        )

    target.write_text(response.text)

    if os_utils.is_root():
        # Fix the permissions of the docker-compose.yml so that the BrainFrame
        # group can edit it
        os_utils.give_brainframe_group_rw_access([target])


def get_latest_version() -> str:
    """
    :return: The latest available version in the format "vX.Y.Z"
    """
    # Add the flags to authenticate with staging if the user wants to download
    # from there
    subdomain = "staging." if config.is_staging.value else ""
    credentials = config.staging_credentials()

    # Check what the latest version is
    url = BRAINFRAME_LATEST_TAG_URL.format(subdomain=subdomain)
    response = requests.get(url, auth=credentials)
    return response.text


def check_existing_version(install_path: Path) -> str:
    compose_path = install_path / "docker-compose.yml"
    compose = yaml.load(compose_path.read_text(), Loader=yaml.SafeLoader)
    version = compose["services"]["core"]["image"].split(":")[-1]
    version = "v" + version
    return version


def assert_has_docker_permissions() -> None:
    """Fails if the user does not have permissions to interact with Docker"""
    if not (os_utils.is_root() or os_utils.currently_in_group("docker")):
        error_message = (
            i18n.t("general.docker-bad-permissions")
            + "\n"
            + _group_recommendation_message("docker")
        )

        print_utils.fail(error_message)


def _assert_has_write_permissions(path: Path) -> None:
    """Fails if the user does not have write access to the given path."""
    if os.access(path, os.W_OK):
        return

    error_message = i18n.t("general.file-bad-write-permissions", path=path)
    error_message += "\n"

    if path.stat().st_gid == os_utils.BRAINFRAME_GROUP_ID:
        error_message += " " + _group_recommendation_message("brainframe")
    else:
        error_message += " " + i18n.t(
            "general.unexpected-group-for-file", path=path, group="brainframe"
        )

    print_utils.fail(error_message)


def _group_recommendation_message(group: str) -> str:
    if os_utils.added_to_group("brainframe"):
        # The user is in the group, they just need to restart
        return i18n.t("general.restart-for-group-access", group=group)
    else:
        # The user is not in the group, so they need to either add
        # themselves or use sudo
        return i18n.t("general.retry-as-root-or-group", group=group)
