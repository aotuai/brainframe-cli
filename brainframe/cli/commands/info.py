from argparse import ArgumentParser

import i18n

from brainframe.cli import env_vars, print_utils, docker_compose
from .utils import subcommand_parse_args, command


@command("info")
def info():
    args = _parse_args()

    docker_compose.assert_installed(env_vars.install_path.get())

    server_version = docker_compose.check_existing_version(
        env_vars.install_path.get()
    )

    fields = {
        "install_path": env_vars.install_path.get(),
        "data_path": env_vars.data_path.get(),
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
