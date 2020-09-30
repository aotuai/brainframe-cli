import sys

import i18n

from brainframe.cli import docker_compose, env_vars, os_utils, print_utils
from .utils import command


@command("compose")
def compose():
    install_path = env_vars.install_path.get()
    docker_compose.assert_installed(install_path)
    docker_compose.run(install_path, sys.argv[2:])
