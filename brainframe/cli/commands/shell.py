from argparse import ArgumentParser

import i18n
from brainframe.cli import brainframe_shell

from .utils import command
from .utils import subcommand_parse_args


@command("shell")
def shell():
    args = _parse_args()
    brainframe_shell.run()


def _parse_args():
    parser = ArgumentParser(
        description=i18n.t("shell.description"), usage=i18n.t("shell.usage")
    )

    return subcommand_parse_args(parser)
