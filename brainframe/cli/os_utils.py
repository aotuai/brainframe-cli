import subprocess
import os
import sys
from typing import List
from pathlib import Path

import i18n
import distro

from . import print_utils


def create_group(group_name):
    # Check if the group exists
    result = run(["getent", "group", group_name], exit_on_failure=False)
    if result.returncode == 0:
        print_utils.translate("install.group-exists")
        return

    # Create the group
    result = run(["groupadd", group_name], root=True)
    if result.returncode != 0:
        message = i18n.t("install.create-group-failure")
        message = message.format(error=str(result.stderr))
        print_utils.fail(message)


def is_in_group(group_name):
    result = run(
        ["groups"],
        stdout=subprocess.PIPE,
        encoding="utf-8",
        print_command=False,
    )
    return group_name in result.stdout.split()


def add_to_group(group_name):
    print_utils.translate("general.adding-to-group", group=group_name)
    result = run(["whoami"], stdout=subprocess.PIPE, encoding="utf-8")
    user = result.stdout.strip()

    run(["usermod", "-a", "-G", group_name, user], root=True)


def is_root():
    return os.geteuid() == 0


def mkdir_root_fallback(path: Path):
    """Makes a directory, asking the user for root permissions if necessary."""
    try:
        path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        # Fall back to bash so we can ask for root permissions
        print_utils.translate(
            "general.mkdir-permission-denied", directory=str(path)
        )
        run(["mkdir", str(path)], root=True)


def run(
    command: List[str],
    root=False,
    print_command=True,
    exit_on_failure=True,
    *args,
    **kwargs,
) -> subprocess.CompletedProcess:
    """A small wrapper around subprocess.run.

    :param command: The command to run
    :param root: If True, ensure the command is run with root permissions
    :param print_command: If True, the command will be printed before being run
    :param exit_on_failure: If True, the application will exit if the command
        results in a non-zero exit code
    """
    if root and not is_root():
        # Ask for root permissions with sudo
        command = ["sudo"] + command

    if print_command:
        print_utils.print_color(" ".join(command), print_utils.Color.MAGENTA)
    result = subprocess.run(command, *args, **kwargs)
    if result.returncode != 0 and exit_on_failure:
        sys.exit(result.returncode)
    return result


_SUPPORTED_DISTROS = {
    "Ubuntu": ["18.04"],
}
"""A dict whose keys are supported Linux distribution names and whose values
are all supported versions for that distribution.
"""


def is_supported() -> bool:
    """
    :return: True if the user is on an officially supported Linux distribution
    """
    name, version, _ = distro.linux_distribution()

    return name in _SUPPORTED_DISTROS and version in _SUPPORTED_DISTROS[name]
