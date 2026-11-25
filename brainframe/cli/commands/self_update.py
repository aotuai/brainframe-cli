import hashlib
import os
import re
import stat
import sys
from argparse import ArgumentParser
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional
from typing import Tuple

import i18n
import requests
from brainframe.cli import __version__
from brainframe.cli import config
from brainframe.cli import frozen_utils
from brainframe.cli import print_utils
from brainframe.cli.network import HTTP_TIMEOUT
from packaging.version import Version

from .utils import command
from .utils import parse_version

_RELEASES_URL_PREFIX = "https://{subdomain}aotu.ai"
_BINARY_URL = "{prefix}/releases/brainframe-cli/brainframe"
_LATEST_TAG_URL = "{prefix}/releases/brainframe-cli/latest"
_CHECKSUM_URL = "{prefix}/releases/brainframe-cli/brainframe.sha256"


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
    if not os.access(executable_path.parent, os.W_OK):
        error_message = i18n.t(
            "general.file-bad-write-permissions", path=executable_path.parent
        )
        error_message += "\n"
        error_message += i18n.t("general.retry-as-root")
        print_utils.fail(error_message)

    credentials = config.staging_credentials()

    prefix = _RELEASES_URL_PREFIX.format(
        subdomain="staging." if config.is_staging.value else ""
    )
    binary_url = _BINARY_URL.format(prefix=prefix)

    current_version = parse_version(__version__)
    latest_version = _latest_version(prefix, credentials)

    if current_version >= latest_version:
        print_utils.fail_translate(
            "self-update.already-up-to-date",
            current_version=current_version,
            latest_version=latest_version,
        )

    checksum_response = requests.get(
        _CHECKSUM_URL.format(prefix=prefix),
        auth=credentials,
        timeout=HTTP_TIMEOUT,
    )
    if not checksum_response.ok or not re.fullmatch(
        r"[0-9a-fA-F]{64}", checksum_response.text.strip()
    ):
        print_utils.fail_translate("self-update.invalid-checksum")
    expected_sha256 = checksum_response.text.strip().lower()

    # Get the updated executable
    print_utils.translate("self-update.downloading")
    response = requests.get(
        binary_url, auth=credentials, stream=True, timeout=HTTP_TIMEOUT
    )
    if not response.ok:
        print_utils.fail_translate(
            "self-update.error-downloading",
            status_code=response.status_code,
            error_message=response.text,
        )

    try:
        _replace_executable(
            executable_path,
            response.iter_content(_BLOCK_SIZE),
            expected_size=(
                int(response.headers["Content-Length"])
                if "Content-Length" in response.headers
                else None
            ),
            expected_sha256=expected_sha256,
        )
    except (ValueError, requests.RequestException) as error:
        print_utils.fail_translate("self-update.invalid-download", error=error)

    print()
    print_utils.translate(
        "self-update.complete", color=print_utils.Color.GREEN
    )


def _replace_executable(
    executable_path: Path, blocks, expected_size=None, expected_sha256=None
) -> None:
    """Write a complete replacement next to the executable, then swap it in."""
    temporary_path = None
    digest = hashlib.sha256()
    size = 0
    header = b""
    try:
        with NamedTemporaryFile(
            "wb",
            prefix=".brainframe-update-",
            dir=str(executable_path.parent),
            delete=False,
        ) as new_executable:
            temporary_path = Path(new_executable.name)
            for block in blocks:
                if not block:
                    continue
                header = (header + block[:4])[:4]
                digest.update(block)
                size += len(block)
                new_executable.write(block)
            if header != b"\x7fELF":
                raise ValueError("download is not an ELF executable")
            if expected_size is not None and size != expected_size:
                raise ValueError("download size differs from Content-Length")
            if (
                expected_sha256 is not None
                and digest.hexdigest() != expected_sha256
            ):
                raise ValueError("download checksum does not match")
            new_executable.flush()
            os.fsync(new_executable.fileno())

        temporary_path.chmod(stat.S_IMODE(executable_path.stat().st_mode))
        os.replace(str(temporary_path), str(executable_path))
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _latest_version(
    url_prefix: str,
    credentials: Optional[Tuple[str, str]],
) -> Version:
    latest_tag_url = _LATEST_TAG_URL.format(prefix=url_prefix)
    response = requests.get(
        latest_tag_url, auth=credentials, timeout=HTTP_TIMEOUT
    )

    if not response.ok:
        print_utils.fail_translate(
            "self-update.error-getting-latest-version",
            status_code=response.status_code,
            error_message=response.text,
        )

    return parse_version(response.text)


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
