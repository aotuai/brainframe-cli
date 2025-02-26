import sys
from argparse import ArgumentParser

import i18n
from brainframe.cli import brainframe_mgmt

from .utils import command
from .utils import subcommand_parse_args


@command("mgmt")
def mgmt():
    if "-h" in sys.argv[2:]:
        args = _parse_args()
    else:
        brainframe_mgmt.run(sys.argv[2:])


def _parse_args():
    parser = ArgumentParser(
        description=i18n.t("mgmt.description"), usage=i18n.t("mgmt.usage")
    )

    return subcommand_parse_args(parser)
