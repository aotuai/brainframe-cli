import os
from pathlib import Path
from typing import Optional, Generic, TypeVar, Callable, Union, Type

T = TypeVar("T")
"""The type of a configuration value"""


class EnvironmentVariable(Generic[T]):
    """Manages a configuration option using system environment variables"""

    def __init__(
        self,
        name,
        default: T = None,
        converter: Union[Type, Callable[[str], T]] = str,
    ):
        """
        :param name: The environment variable name
        :param default: The default value if the variable is unset
        :param converter: Converts the string value of the environment variable
            to the desired type
        """
        self.name = name
        self.default = default
        self.converter = converter

    def get(self) -> Optional[T]:
        if self.name in os.environ:
            value = os.environ[self.name]
            if value is None:
                return None
            return self.converter(value)

        return self.default

    def is_set(self) -> bool:
        return self.name in os.environ


install_path = EnvironmentVariable[Path](
    "BRAINFRAME_INSTALL_PATH",
    default=Path("/usr/local/share/brainframe/"),
    converter=Path,
)

data_path = EnvironmentVariable[Path](
    "BRAINFRAME_DATA_PATH",
    default=Path("/var/local/brainframe"),
    converter=Path,
)

is_staging = EnvironmentVariable[str]("BRAINFRAME_STAGING")
staging_username = EnvironmentVariable[str]("BRAINFRAME_STAGING_USERNAME")
staging_password = EnvironmentVariable[str]("BRAINFRAME_STAGING_PASSWORD")
