import os
from distutils.util import strtobool
from pathlib import Path
from typing import Callable
from typing import Dict
from typing import Generic
from typing import Optional
from typing import Tuple
from typing import TypeVar
from typing import Union

import yaml

from . import frozen_utils
from . import print_utils

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

    def __init__(self, name: str):
        self.name = name

    @property
    def env_var_name(self):
        return "BRAINFRAME_" + self.name.upper()

    def load(
        self, converter: Callable[[str], T], defaults: Dict[str, str]
    ) -> None:
        default = defaults.get(self.name)

        value: Optional[str] = os.environ.get(self.env_var_name, default)

        self.value = None if value is None else converter(value)
        self.default = None if default is None else converter(default)


install_path = Option[Path]("install_path")
data_path = Option[Path]("data_path")

is_staging = Option[bool]("staging")
staging_username = Option[str]("staging_username")
staging_password = Option[str]("staging_password")


def load() -> None:
    """Initializes configuration options"""
    with frozen_utils.DEFAULTS_FILE_PATH.open("r") as defaults_file:
        defaults = yaml.load(defaults_file, Loader=yaml.FullLoader)

    install_path.load(Path, defaults)
    data_path.load(Path, defaults)

    is_staging.load(_bool_converter, defaults)
    staging_username.load(str, defaults)
    staging_password.load(str, defaults)


def staging_credentials() -> Optional[Tuple[str, str]]:
    if not is_staging.value:
        return None

    username = staging_username.value
    password = staging_password.value
    if username is None or password is None:
        print_utils.fail_translate(
            "general.staging-missing-credentials",
            username_env_var=staging_username.env_var_name,
            password_env_var=staging_password.env_var_name,
        )

    # Mypy doesn't understand that fail_translate exits this function, so it
    # thinks the return type should be Tuple[Optional[str], Optional[str]]
    return username, password  # type: ignore


def _bool_converter(value: Union[str, bool]) -> bool:
    if isinstance(value, bool):
        return value

    return bool(strtobool(value))
