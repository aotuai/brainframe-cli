from pathlib import Path
from argparse import ArgumentParser
import sys
from datetime import datetime

import i18n

from brainframe.cli import print_utils, docker_compose, os_utils, dependencies
from .utils import subcommand_parse_args


BACKUP_DIR_FORMAT = "%Y-%m-%d_%H-%M-%S"


def backup(install_path: Path, data_path: Path):
    args = _parse_args(data_path)

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

    print("")
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
        help=i18n.t("backup.noninteractive_help"),
    )

    parser.add_argument(
        "--install-rsync",
        action="store_true",
        help=i18n.t("backup.install-rsync-help"),
    )

    return subcommand_parse_args(parser)
