import sys

from brainframe.cli import config, docker_compose

from .utils import command


@command("compose")
def compose():
    install_path = config.install_path.value
    docker_compose.assert_installed(install_path)
    docker_compose.run(install_path, sys.argv[2:])
