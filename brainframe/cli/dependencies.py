import shutil

from . import os_utils, print_utils


class Dependency:
    """Provides functionality for discovering and installing an executable that
    the CLI depends on
    """

    def __init__(self, command_name, ask_message, install_func):
        self.command_name = command_name
        self.ask_message = ask_message
        self.install = install_func

    def ensure(self, noninteractive: bool, install_requested: bool):
        """Ensures that this dependency is installed, installing it if we're
        running on a supported OS and the user opts in. Exits with an error
        code if the dependency could not be ensured.

        :param noninteractive: If true, the user will not be prompted
        :param install_requested: If true, the user opted in to automatic
            noninteractive installation
        """
        # Only supported operating systems can request automatic installs
        if install_requested and not os_utils.is_supported():
            print_utils.fail_translate(
                "install.install-dependency-unsupported-os"
            )

        if shutil.which(self.command_name) is not None:
            # The command is already installed
            return

        print_utils.translate(
            "install.missing-dependency", dependency=self.command_name
        )

        if noninteractive:
            install = install_requested
        elif os_utils.is_supported():
            install = print_utils.ask_yes_no(self.ask_message)
        else:
            install = False

        if install:
            self.install()
        else:
            # The dependency is missing and we can't automatically install it.
            # Quit out with an error.
            print_utils.fail_translate(
                "install.install-dependency-manually",
                dependency=self.command_name,
            )


def _install_docker():
    os_utils.run(
        ["curl", "-fsSL", "https://get.docker.com", "-o", "/tmp/get-docker.sh"]
    )
    os_utils.run(["sh", "/tmp/get-docker.sh"])


docker = Dependency("docker", "install.ask-install-docker", _install_docker,)

rsync = Dependency(
    "rsync",
    "install.ask-install-rsync",
    lambda: os_utils.run(["apt-get", "install", "-y", "rsync"]),
)

curl = Dependency(
    "curl",
    "install.ask-install-curl",
    lambda: os_utils.run(["apt-get", "install", "-y", "curl"]),
)
