import getpass
import os
import subprocess
import sys

import i18n
import requests
import yaml

from . import os_utils
from . import print_utils
from .brainframe_compose import assert_has_docker_permissions


def run() -> None:
    assert_has_docker_permissions()

    image_name = "aotuai/brainframe-cli-20.04:0.3.2"
    host_user = getpass.getuser()
    host_dir = os.getcwd()
    full_command = f"docker run -it --rm -v {host_dir}:/host -w /host -e HOST_USER={host_user} {image_name} bash"

    print_utils.translate(full_command, color=print_utils.Color.GREEN)

    try:
        subprocess.run(full_command, shell=True, check=True)
    except Exception as e:  # subprocess.CalledProcessError:
        print(f"Error: Failed to pull or run the image. Details: {e}")
        sys.exit(1)
