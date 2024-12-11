from argparse import ArgumentParser

import i18n
from brainframe.cli import brainframe_compose
from brainframe.cli import config
from brainframe.cli import print_utils

from .utils import command
from .utils import subcommand_parse_args


@command("info")
def info():
    args = _parse_args()

    brainframe_compose.assert_installed(config.install_path.value)

    server_version = brainframe_compose.check_existing_version(
        config.install_path.value
    )

    fields = {
        "install_path": config.install_path.value,
        "data_path": config.data_path.value,
        "server_version": server_version,
    }

    if args.field is None:
        # Print all fields
        for name, value in fields.items():
            print(f"{name}: {value}")
    elif args.field in fields:
        # Print just this field's value
        print(fields[args.field])
    else:
        print_utils.fail_translate("info.no-such-field", field=args.field)


def _parse_args():
    parser = ArgumentParser(
        description=i18n.t("info.description"), usage=i18n.t("info.usage")
    )

    parser.add_argument(
        "field", default=None, nargs="?", help=i18n.t("info.field-help")
    )

    return subcommand_parse_args(parser)
