import os
from pathlib import Path
from typing import Generic, Optional, TypeVar

import yaml
from distutils.util import strtobool

from . import print_utils

_DEFAULTS_FILE_PATH = Path(__file__).parent / "defaults.yaml"


T = TypeVar("T")


class Option(Generic[T]):
    """A configuration option.

    Option values are determined using the following precedence:
      1. From an environment variable with the name "BRAINFRAME_" followed by the option
         name in all caps
      2. From the defaults file shipped with this distribution
      3. The fallback value, which is None
    """

    name: str
    value: Optional[T] = None
    default: Optional[T] = None

    def __init__(self, name):
        self.name = name

    def load(self, converter, defaults):
        default = defaults.get(self.name)
        env_var_name = "BRAINFRAME_" + self.name.upper()
        if env_var_name in os.environ:
            value = os.environ[env_var_name]
        else:
            value = default

        self.value = None if value is None else converter(value)
        self.default = None if default is None else converter(default)


install_path = Option[Path]("install_path")
data_path = Option[Path]("data_path")

is_staging = Option[bool]("staging")
staging_username = Option[str]("staging_username")
staging_password = Option[str]("staging_password")


def load():
    """Initializes configuration options"""
    if not _DEFAULTS_FILE_PATH.is_file():
        print_utils.fail_translate(
            "general.missing-defaults-file",
            defaults_file_path=_DEFAULTS_FILE_PATH,
        )

    with _DEFAULTS_FILE_PATH.open("r") as defaults_file:
        defaults = yaml.load(defaults_file, Loader=yaml.FullLoader)

    install_path.load(Path, defaults)
    data_path.load(Path, defaults)

    is_staging.load(strtobool, defaults)
    staging_username.load(str, defaults)
    staging_password.load(str, defaults)
