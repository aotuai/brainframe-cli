import os
import subprocess
import sys
from pathlib import Path
from typing import List, TextIO, Tuple, cast

import i18n
import yaml

from . import config, os_utils, print_utils

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


def run(install_path: Path, commands: List[str]) -> None:
    _assert_has_docker_permissions()

    compose_path = install_path / "docker-compose.yml"

    full_command = [
        sys.executable,
        "-m",
        "compose",
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

    os_utils.run(full_command + commands)


def download(target: Path, version: str = "latest") -> None:
    _assert_has_write_permissions(target.parent)

    subdomain, auth_flags, version = check_download_version(version=version)

    url = BRAINFRAME_DOCKER_COMPOSE_URL.format(
        subdomain=subdomain, version=version
    )
    os_utils.run(
        ["curl", "-o", str(target), "--fail", "--location", url] + auth_flags,
    )

    if os_utils.is_root():
        # Fix the permissions of the docker-compose.yml so that the BrainFrame
        # group can edit it
        os_utils.give_brainframe_group_rw_access([target])


def check_download_version(
    version: str = "latest",
) -> Tuple[str, List[str], str]:
    subdomain = ""
    auth_flags = []

    # Add the flags to authenticate with staging if the user wants to download
    # from there
    if config.is_staging.value:
        subdomain = "staging."

        username = config.staging_username.value
        password = config.staging_password.value
        if username is None or password is None:
            print_utils.fail_translate(
                "general.staging-missing-credentials",
                username_env_var=config.staging_username.name,
                password_env_var=config.staging_password.name,
            )

        auth_flags = ["--user", f"{username}:{password}"]

    if version == "latest":
        # Check what the latest version is
        url = BRAINFRAME_LATEST_TAG_URL.format(subdomain=subdomain)
        result = os_utils.run(
            ["curl", "--fail", "-s", "--location", url] + auth_flags,
            print_command=False,
            stdout=subprocess.PIPE,
            encoding="utf-8",
        )
        # stdout is a file-like object opened in text mode when the encoding
        # argument is "utf-8"
        stdout = cast(TextIO, result.stdout)
        version = stdout.readline().strip()

    return subdomain, auth_flags, version


def check_existing_version(install_path: Path) -> str:
    compose_path = install_path / "docker-compose.yml"
    compose = yaml.load(compose_path.read_text(), Loader=yaml.SafeLoader)
    version = compose["services"]["core"]["image"].split(":")[-1]
    version = "v" + version
    return version


def _assert_has_docker_permissions() -> None:
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
