import os
import subprocess
import sys
from pathlib import Path
from threading import RLock
from typing import List
from typing import Optional

import distro
import i18n

from . import print_utils

BRAINFRAME_GROUP_ID = 1337
"""An arbitrary group ID value for the 'brainframe' group. We have to specify
the ID of the group manually to ensure that the host machine and the Docker
containers agree on it.
"""


class _CurrentCommand:
    """Contains information on the current command being run as a subprocess, if one
    exists.
    """

    _process: Optional[subprocess.Popen] = None
    _lock = RLock()
    _interrupted = False

    @property
    def process(self) -> Optional[subprocess.Popen]:
        """
        :return: The currently running subprocess, or None if no subprocess is running
        """
        with self._lock:
            return self._process

    @process.setter
    def process(self, value: subprocess.Popen) -> None:
        with self._lock:
            if self._process is not None and self._process.poll() is None:
                # This is never expected to happen, as subprocesses are run in serial
                # and in a blocking fashion
                raise RuntimeError("Only one process may be run at once")

            self._process = value

    @property
    def interrupted(self) -> bool:
        """
        :return: If true, the subprocess was interrupted by a signal
        """
        return self._interrupted

    def send_signal(self, sig: int):
        """
        :param sig: The signal to send to the subprocess
        """
        with self._lock:
            if self._process is None:
                message = (
                    "Attempted to send a signal when no process was running"
                )
                raise RuntimeError(message)
            self._interrupted = True
            self._process.send_signal(sig)


current_command = _CurrentCommand()


def create_group(group_name: str, group_id: int):
    # Check if the group exists
    result = run(["getent", "group", group_name], exit_on_failure=False)
    if result.returncode == 0:
        print_utils.translate("install.group-exists")
        return

    # Create the group
    result = run(["groupadd", group_name, "--gid", str(group_id)])
    if result.returncode != 0:
        print_utils.fail_translate(
            "install.create-group-failure", error=str(result.stderr)
        )


def added_to_group(group_name):
    """Checks if the user has been added to the group, even if the group
    addition hasn't been applied yet (i.e. by re-logging). Compare to
    `currently_in_group`.
    """
    result = run(
        ["id", "-Gn", _current_user()],
        stdout=subprocess.PIPE,
        encoding="utf-8",
        print_command=False,
    )
    return group_name in result.stdout.readline().split()


def currently_in_group(group_name):
    """Checks if the user is currently in the group. This will be False if the
    user was added to the group but the change hasn't been applied yet. Compare
    to `added_to_group`.
    """
    result = run(
        ["id", "-Gn"],
        stdout=subprocess.PIPE,
        encoding="utf-8",
        print_command=False,
    )
    return group_name in result.stdout.readline().split()


def add_to_group(group_name):
    print_utils.translate("general.adding-to-group", group=group_name)
    run(["usermod", "-a", "-G", group_name, _current_user()])


def is_root():
    return os.geteuid() == 0


def give_brainframe_group_rw_access(paths: List[Path]):
    paths_str = [str(p) for p in paths]

    run(["chgrp", "-R", "brainframe"] + paths_str)
    run(["chmod", "-R", "g+rw"] + paths_str)


def _current_user():
    # If the SUDO_USER environment variable allows us to get the username of
    # the user running sudo instead of root. If they're not using sudo, we can
    # just pull the username from $LOGNAME.
    # "Why not use $USER here?" you might ask. Apparently $LOGNAME is a
    # POSIX standard and $USER is not.
    #  https://unix.stackexchange.com/a/76369/117461
    return os.environ.get("SUDO_USER", os.environ["LOGNAME"])


def run(
    command: List[str],
    print_command=True,
    exit_on_failure=True,
    *args,
    **kwargs,
) -> subprocess.Popen:
    """A small wrapper around subprocess.run.

    :param command: The command to run
    :param print_command: If True, the command will be printed before being run
    :param exit_on_failure: If True, the application will exit if the command
        results in a non-zero exit code
    """
    if print_command:
        print_utils.print_color(" ".join(command), print_utils.Color.MAGENTA)

    current_command.process = subprocess.Popen(command, *args, **kwargs)
    current_command.process.wait()

    if current_command.interrupted:
        # A signal was sent to the command before it finished
        print_utils.fail_translate("general.interrupted")
    elif current_command.process.returncode != 0 and exit_on_failure:
        # The command failed during normal execution
        sys.exit(current_command.process.returncode)

    return current_command.process


_SUPPORTED_DISTROS = {
    "Ubuntu": ["18.04", "20.04"],
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
