import shutil
from argparse import ArgumentParser

import i18n
from brainframe.cli import docker_compose, env_vars, os_utils, print_utils

from .utils import command, subcommand_parse_args


@command("uninstall")
def uninstall():
    install_path = env_vars.install_path.get()
    data_path = env_vars.data_path.get()

    args = _parse_args()

    # This command has to be run as root so that the "brainframe" group can be
    # deleted, and because some BrainFrame services write files as the root
    # user.
    if not os_utils.is_root():
        print_utils.fail_translate("general.user-not-root")

    docker_compose.assert_installed(install_path)

    if not args.noninteractive:
        print_utils.warning_translate(
            "uninstall.warning",
            directories=[str(install_path), str(data_path)],
        )
        confirmed = print_utils.ask_yes_no("uninstall.ask-confirm")
        if not confirmed:
            print_utils.fail_translate("uninstall.abort")

    print_utils.translate("uninstall.deleting-images")
    docker_compose.run(install_path, ["down", "--rmi", "all"])
    print_utils.translate("uninstall.deleting-install-path")
    shutil.rmtree(install_path)
    print_utils.translate("uninstall.deleting-data-path")
    shutil.rmtree(data_path)
    print_utils.translate("uninstall.deleting-group")
    os_utils.delete_group("brainframe")

    print()
    print_utils.translate("uninstall.complete", color=print_utils.Color.GREEN)


def _parse_args():
    parser = ArgumentParser(
        description=i18n.t("uninstall.description"),
        usage=i18n.t("uninstall.usage"),
    )

    parser.add_argument(
        "--noninteractive",
        action="store_true",
        help=i18n.t("general.noninteractive-help"),
    )

    return subcommand_parse_args(parser)
