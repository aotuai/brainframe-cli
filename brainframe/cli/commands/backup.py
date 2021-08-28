import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

import i18n
from brainframe.cli import (
    config,
    dependencies,
    docker_compose,
    os_utils,
    print_utils,
)

from .utils import command, subcommand_parse_args

BACKUP_DIR_FORMAT = "%Y-%m-%d_%H-%M-%S"


@command("backup")
def backup():
    install_path = config.install_path.value
    data_path = config.data_path.value

    args = _parse_args(data_path)

    # This command has to be run as root for now because some BrainFrame
    # services write files as the root user.
    if not os_utils.is_root():
        print_utils.fail_translate("general.user-not-root")

    docker_compose.assert_installed(install_path)

    dependencies.rsync.ensure(args.noninteractive, args.install_rsync)

    if not args.noninteractive:
        stop_brainframe = print_utils.ask_yes_no("backup.ask-stop-brainframe")
        if not stop_brainframe:
            # BrainFrame needs to be stopped before a backup. If the user
            # doesn't want that, stop the backup
            sys.exit(1)

    docker_compose.run(install_path, ["stop"])

    if args.destination is None:
        now_str = datetime.now().strftime(BACKUP_DIR_FORMAT)
        backup_path = data_path / "backups" / now_str
    else:
        backup_path = args.destination

    try:
        backup_path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        print_utils.fail_translate("backup.mkdir-permission-denied")

    os_utils.run(
        [
            "rsync",
            "--archive",
            "--verbose",
            "--progress",
            # Avoid backing up backups
            "--exclude",
            "backups",
            str(data_path),
            str(backup_path),
        ]
    )

    # Give the brainframe group access to the resulting backup, to make
    # managing and restoring it easier
    os_utils.give_brainframe_group_rw_access([backup_path])

    print()
    print_utils.translate("backup.complete", color=print_utils.Color.GREEN)


def _parse_args(data_path: Path):
    parser = ArgumentParser(
        description=i18n.t("backup.description"), usage=i18n.t("backup.usage")
    )

    parser.add_argument(
        "--destination",
        type=Path,
        help=i18n.t(
            "backup.destination-help", backup_dir=data_path / "backups"
        ),
    )

    parser.add_argument(
        "--noninteractive",
        action="store_true",
        help=i18n.t("general.noninteractive-help"),
    )

    parser.add_argument(
        "--install-rsync",
        action="store_true",
        help=i18n.t("backup.install-rsync-help"),
    )

    return subcommand_parse_args(parser)
