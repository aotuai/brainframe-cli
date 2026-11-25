import os
import shlex
import subprocess
import sys

from . import os_utils
from . import print_utils
from .brainframe_compose import assert_has_docker_permissions


def run() -> None:
    assert_has_docker_permissions()

    image_name = os.environ.get(
        "BRAINFRAME_SHELL_IMAGE", "aotuai/brainframe-cli-20.04:0.3.2"
    )
    host_user = os_utils._current_user()
    host_dir = os.getcwd()
    full_command = [
        "docker",
        "run",
        "-it",
        "--rm",
        "-v",
        "{}:/host".format(host_dir),
        "-w",
        "/host",
        "-e",
        "HOST_USER={}".format(host_user),
        image_name,
    ]

    print_utils.translate(
        " ".join(shlex.quote(part) for part in full_command),
        color=print_utils.Color.GREEN,
    )

    try:
        subprocess.run(full_command, check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"Error: Failed to pull or run the image. Details: {e}")
        sys.exit(1)
