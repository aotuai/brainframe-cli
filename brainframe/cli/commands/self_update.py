import os
import shutil
import stat
import sys
from argparse import ArgumentParser
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional
from typing import Tuple
from typing import Union

import i18n
import requests
from brainframe.cli import __version__
from brainframe.cli import config
from brainframe.cli import frozen_utils
from brainframe.cli import print_utils
from packaging import version

from .utils import command

_RELEASES_URL_PREFIX = "https://{subdomain}aotu.ai"
_BINARY_URL = "{prefix}/releases/brainframe-cli/brainframe"
_LATEST_TAG_URL = "{prefix}/releases/brainframe-cli/latest"


@command("self-update")
def self_update():
    _parse_args()

    if not frozen_utils.is_frozen():
        print_utils.fail_translate("self-update.not-frozen")

    executable_path = Path(sys.executable)

    # Check if the user has permissions to overwrite the executable in its
    # current location
    if not os.access(executable_path, os.W_OK):
        error_message = i18n.t(
            "general.file-bad-write-permissions", path=executable_path
        )
        error_message += "\n"
        error_message += i18n.t("general.retry-as-root")
        print_utils.fail(error_message)

    credentials = config.staging_credentials()

    prefix = _RELEASES_URL_PREFIX.format(
        subdomain="staging." if config.is_staging.value else ""
    )
    binary_url = _BINARY_URL.format(prefix=prefix)

    current_version = version.parse(__version__)
    latest_version = _latest_version(prefix, credentials)

    if current_version >= latest_version:
        print_utils.fail_translate(
            "self-update.already-up-to-date",
            current_version=current_version,
            latest_version=latest_version,
        )

    # Get the updated executable
    print_utils.translate("self-update.downloading")
    response = requests.get(binary_url, auth=credentials, stream=True)
    if not response.ok:
        print_utils.fail_translate(
            "self-update.error-downloading",
            status_code=response.status_code,
            error_message=response.text,
        )

    with NamedTemporaryFile("wb") as new_executable:
        for block in response.iter_content(_BLOCK_SIZE):
            new_executable.write(block)
        new_executable.flush()

        # Set the result as executable
        current_stat = executable_path.stat()
        executable_path.chmod(
            current_stat.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )

        # Overwrite the existing executable with the new one
        # Really excited for copy3, coming this summer
        shutil.copy2(new_executable.name, executable_path)

    print()
    print_utils.translate(
        "self-update.complete", color=print_utils.Color.GREEN
    )


def _latest_version(
    url_prefix: str,
    credentials: Optional[Tuple[str, str]],
) -> Union[version.LegacyVersion, version.Version]:
    latest_tag_url = _LATEST_TAG_URL.format(prefix=url_prefix)
    response = requests.get(latest_tag_url, auth=credentials)

    if not response.ok:
        print_utils.fail_translate(
            "self-update.error-getting-latest-version",
            status_code=response.status_code,
            error_message=response.text,
        )

    return version.parse(response.text)


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
