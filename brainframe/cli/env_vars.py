import os
from pathlib import Path
from typing import Callable, Generic, Optional, Type, TypeVar, Union

import yaml

T = TypeVar("T")
"""The type of a configuration value"""


_CONFIG_FILE_PATH = Path(__file__).parent / "defaults.yaml"


class EnvironmentVariable(Generic[T]):
    """Manages a configuration option whose value can come from multiple sources.

    The value is pulled from these sources, in order of priority:
      1. Environment variable
      2. Defaults configuration file
      3. Default value
    """

    def __init__(
        self,
        name: str,
        default: T = None,
        converter: Union[Type, Callable[[str], T]] = str,
    ):
        """
        :param name: The environment variable name
        :param default: The default value if no other sources are available
        :param converter: Converts the string value of the environment variable
            to the desired type
        """
        self.name = name
        self.default = default
        self.converter = converter

    def get(self) -> Optional[T]:
        try:
            return self._get_env_var()
        except _NoConfigValueError:
            pass

        try:
            return self._get_config_file()
        except _NoConfigValueError:
            pass

        return self.default

    def is_set(self) -> bool:
        return self.name in os.environ

    def _get_env_var(self):
        if self._env_var_name in os.environ:
            value = os.environ[self._env_var_name]
            if value is None:
                return None
            return self.converter(value)
        else:
            raise _NoConfigValueError()

    def _get_config_file(self):
        try:
            with _CONFIG_FILE_PATH.open("r") as config_file:
                config = yaml.load(config_file, Loader=yaml.FullLoader)
        except FileNotFoundError:
            raise _NoConfigValueError()

        if self.name in config:
            return self.converter(config[self.name])

        raise _NoConfigValueError()

    @property
    def _env_var_name(self):
        return "BRAINFRAME_" + self.name.upper()


install_path = EnvironmentVariable[Path](
    "install_path",
    default=Path("/usr/local/share/brainframe/"),
    converter=Path,
)

data_path = EnvironmentVariable[Path](
    "data_path",
    default=Path("/var/local/brainframe"),
    converter=Path,
)

is_staging = EnvironmentVariable[str]("staging")
staging_username = EnvironmentVariable[str]("staging_username")
staging_password = EnvironmentVariable[str]("staging_password")


class _NoConfigValueError(Exception):
    """Raised when a configuration value is unavailable from a source"""
