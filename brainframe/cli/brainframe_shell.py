import os
import subprocess
import sys
import getpass

import i18n
import requests
import yaml

from .brainframe_compose import assert_has_docker_permissions
from . import os_utils
from . import print_utils


def run() -> None:
    assert_has_docker_permissions()

    image_name = "aotuai/brainframe-cli-20.04:0.3.1"
    host_user = getpass.getuser()
    full_command = f"docker run -it --rm -v .:/host -w /host -e HOST_USER={host_user} {image_name} bash"

    print_utils.translate(full_command, color=print_utils.Color.GREEN)

    try:
        subprocess.run(full_command, shell=True, check=True)
    except Exception as e: # subprocess.CalledProcessError:
        print(f"Error: Failed to pull or run the image. Details: {e}")
        sys.exit(1)

