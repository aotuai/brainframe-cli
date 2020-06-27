import subprocess
import os
import sys
from pathlib import Path
from typing import List

import i18n
import distro

from . import print_utils


BRAINFRAME_GROUP_ID = 1386


def create_group(group_name: str, group_id: int):
    # Check if the group exists
    result = run(["getent", "group", group_name], exit_on_failure=False)
    if result.returncode == 0:
        print_utils.translate("install.group-exists")
        return

    # Create the group
    result = run(["groupadd", group_name, "--gid", str(group_id)])
    if result.returncode != 0:
        message = i18n.t("install.create-group-failure")
        message = message.format(error=str(result.stderr))
        print_utils.fail(message)


def is_in_group(group_name):
    result = run(
        ["groups", _current_user()],
        stdout=subprocess.PIPE,
        encoding="utf-8",
        print_command=False,
    )
    return group_name in result.stdout.split()


def add_to_group(group_name):
    print_utils.translate("general.adding-to-group", group=group_name)
    run(["usermod", "-a", "-G", group_name, _current_user()])


def is_root():
    return os.geteuid() == 0


def give_brainframe_group_rw_access(paths: List[Path]):
    paths_str = [str(p) for p in paths]

    run(["chgrp", "-R", "brainframe"] + paths_str)
    run(["chmod", "g+rwx"] + paths_str)


def _current_user():
    if "SUDO_USER" in os.environ:
        # The user is running with sudo. Use $SUDO_USER to get the username of
        # the user running sudo instead of root.
        return os.environ["SUDO_USER"]
    else:
        # "Why not use $USER here?" you might ask. Apparently $LOGNAME is a
        # POSIX standard and $USER is not.
        # https://unix.stackexchange.com/a/76369/117461
        return os.environ["LOGNAME"]


def run(
    command: List[str],
    print_command=True,
    exit_on_failure=True,
    *args,
    **kwargs,
) -> subprocess.CompletedProcess:
    """A small wrapper around subprocess.run.

    :param command: The command to run
    :param print_command: If True, the command will be printed before being run
    :param exit_on_failure: If True, the application will exit if the command
        results in a non-zero exit code
    """
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
