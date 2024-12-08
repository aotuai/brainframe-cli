import sys

from brainframe.cli import config, brainframe_compose

from .utils import command


@command("compose")
def compose():
    install_path = config.install_path.value
    brainframe_compose.assert_installed(install_path)
    brainframe_compose.run(install_path, sys.argv[2:])
