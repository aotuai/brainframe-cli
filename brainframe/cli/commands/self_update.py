import os
import stat
import sys
from argparse import ArgumentParser
from pathlib import Path

import i18n
import requests
from brainframe.cli import frozen_utils, print_utils

from .utils import command


@command("self-update")
def self_update():
    _parse_args()

    if not frozen_utils.is_frozen():
        print_utils.fail_translate("self-update.not-frozen")

    executable_path = Path(sys.executable)

    # Check if the user has permissions to overwrite the executable in its
    # current location
    if not os.access(executable_path, os.W_OK):
        error_message = i18n.t("general.file-bad-write-permissions")
        error_message += "\n"
        error_message += i18n.t("general.retry-as-root")
        print_utils.fail(error_message)

    # Get the updated executable
    print_utils.translate("self-update.downloading")
    response = requests.get("http://localhost/brainframe", stream=True)
    if not response.ok:
        print_utils.fail_translate(
            "self-update.error-downloading",
            status_code=response.status_code,
            error_message=response.text,
        )

    # Overwrite the existing executable with the new one
    os.remove(executable_path)
    with executable_path.open("wb") as file_:
        for block in response.iter_content(_BLOCK_SIZE):
            file_.write(block)

    # Set the result as executable
    current_stat = os.stat(executable_path)
    os.chmod(
        executable_path,
        current_stat.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
    )

    print()
    print_utils.translate(
        "self-update.complete", color=print_utils.Color.GREEN
    )


def _parse_args():
    parser = ArgumentParser(
        description=i18n.t("self-update.description"),
        usage=i18n.t("self-update.usage"),
    )

    return parser.parse_args(sys.argv[2:])


_BLOCK_SIZE = 1024000
"""The block size to read files at. Chosen from this answer:
https://stackoverflow.com/a/3673731
"""
