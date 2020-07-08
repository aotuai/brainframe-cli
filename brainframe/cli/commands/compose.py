import sys

import i18n

from brainframe.cli import docker_compose, env_vars, os_utils, print_utils
from .utils import command


@command("compose")
def compose():
    # Check first if the user has permission to interact with Docker
    if not os_utils.is_root():
        if not os_utils.currently_in_group("docker"):
            error_message = i18n.t("compose.docker-bad-permissions") + "\n"

            if os_utils.added_to_group("docker"):
                # The user is in the group, they just need to restart
                error_message += i18n.t("compose.restart-for-group-access")
            else:
                # The user is not in the group, so they need to either add
                # themselves or use sudo
                error_message += i18n.t("compose.retry-with-sudo-or-group")

            print_utils.fail(error_message)

    install_path = env_vars.install_path.get()
    docker_compose.assert_installed(install_path)
    docker_compose.run(install_path, sys.argv[2:])
