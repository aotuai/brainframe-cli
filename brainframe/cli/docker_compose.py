import os
import subprocess
from pathlib import Path
from typing import List, TextIO, Tuple, cast
import platform

import i18n
import yaml
from packaging.version import Version

from . import env_vars, os_utils, print_utils

# The URL to the docker-compose.yml
BRAINFRAME_DOCKER_COMPOSE_URL = "https://{subdomain}aotu.ai/releases/brainframe/{version}/docker-compose.yml"
# The URL to the latest tag, which is just a file containing the latest version
# as a string
BRAINFRAME_LATEST_TAG_URL = (
    "https://{subdomain}aotu.ai/releases/brainframe/latest"
)
# The required Docker Compose executable version
TOOL_VERSION = Version("1.27.4")
# The URL to download the Docker Compose executable from
TOOL_URL = (
    "https://github.com/docker/compose/releases/download/"
    "{version}/docker-compose-{os}-{architecture}"
)


def assert_installed(install_path: Path) -> None:
    compose_path = install_path / "docker-compose.yml"

    if not compose_path.is_file():
        print_utils.fail_translate(
            "general.brainframe-must-be-installed",
            install_env_var=env_vars.install_path.name,
        )


def run(install_path: Path, commands: List[str]) -> None:
    _assert_has_docker_permissions()
    tool_path = _assert_tool_installed(install_path)

    compose_path = install_path / "docker-compose.yml"

    full_command = [str(tool_path), "--file", str(compose_path)]

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
    if env_vars.is_staging.is_set():
        subdomain = "staging."

        username = env_vars.staging_username.get()
        password = env_vars.staging_password.get()
        if username is None or password is None:
            print_utils.fail_translate(
                "general.staging-missing-credentials",
                username_env_var=env_vars.staging_username.name,
                password_env_var=env_vars.staging_password.name,
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


def _assert_tool_installed(install_path: Path) -> Path:
    """Checks if Docker Compose is installed and at the desired version, and
    installs it if not.

    :param install_path: The configured install path
    :return: The path to the Docker Compose executable
    """
    tool_path = (install_path / "docker-compose").absolute()

    if not tool_path.is_file():
        print_utils.translate(
            "general.downloading-docker-compose-tool", version=TOOL_VERSION
        )
        _install_tool(tool_path)
    elif TOOL_VERSION > _get_tool_version(tool_path):
        print_utils.translate(
            "general.updating-docker-compose-tool", version=TOOL_VERSION
        )
        _install_tool(tool_path)

    return tool_path


def _install_tool(tool_path: Path) -> None:
    """Installs Docker Compose.

    :param tool_path: The path to install Docker Compose to
    """
    # Fill in the Docker Compose download URL with the desired version and
    # information about this machine
    tool_url = TOOL_URL.format(
        version=TOOL_VERSION,
        os=platform.system(),
        architecture=platform.machine(),
    )

    os_utils.run(["curl", "-L", tool_url, "-o", str(tool_path)])
    os_utils.run(["chmod", "+x", str(tool_path)])

    if os_utils.is_root():
        # Fix the permissions of the Docker Compose executable so that the
        # "brainframe" group can edit it
        os_utils.give_brainframe_group_rw_access([tool_path])


def _get_tool_version(tool_path: Path) -> Version:
    """
    :param tool_path: The path to the Docker Compose executable
    :return: The currently installed Docker Compose version
    """
    result = os_utils.run(
        [str(tool_path), "version", "--short"],
        print_command=False,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )

    # stdout is a file-like object opened in text mode when the encoding
    # argument is "utf-8"
    stdout = cast(TextIO, result.stdout)
    version_str = stdout.readline().strip()

    return Version(version_str)
