import sys
from argparse import ArgumentParser

import i18n

from brainframe.cli import brainframe_kits

from .utils import command, subcommand_parse_args


@command("kits")
def kits():
    if "-h" in sys.argv[2:]:
        args = _parse_args()
    else:
        brainframe_kits.run(sys.argv[2:])


def _parse_args():
    parser = ArgumentParser(
        description=i18n.t("kits.description"), usage=i18n.t("kits.usage")
    )

    return subcommand_parse_args(parser)
