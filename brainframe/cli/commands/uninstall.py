import shutil
from argparse import ArgumentParser

import i18n
from brainframe.cli import config, docker_compose, os_utils, print_utils

from .utils import command, subcommand_parse_args, requires_root


@command("uninstall")
@requires_root
def uninstall():
    install_path = config.install_path.value
    data_path = config.data_path.value

    args = _parse_args()

    docker_compose.assert_installed(install_path)

    if args.noninteractive:
        delete_data = args.delete_data
    else:
        delete_data = print_utils.ask_yes_no("uninstall.ask-delete-data")

    if not args.noninteractive:
        directories_to_delete = [str(install_path)]
        if delete_data:
            print_utils.warning_translate("uninstall.warning-with-delete-data")
            directories_to_delete.append(str(data_path))
        else:
            print_utils.warning_translate("uninstall.warning")

        print_utils.warning_translate(
            "uninstall.directories-deleted", directories=directories_to_delete,
        )
        confirmed = print_utils.ask_yes_no("uninstall.ask-confirm")
        if not confirmed:
            print_utils.fail_translate("uninstall.abort")

    print_utils.translate("uninstall.deleting-images")
    docker_compose.run(install_path, ["down", "--rmi", "all"])
    print_utils.translate("uninstall.deleting-install-path")
    shutil.rmtree(install_path)
    if delete_data:
        print_utils.translate("uninstall.deleting-data-path")
        shutil.rmtree(data_path)

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

    parser.add_argument(
        "--delete-data",
        action="store_true",
        help=i18n.t("uninstall.delete-data-help"),
    )

    return subcommand_parse_args(parser)
