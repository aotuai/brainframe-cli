import os
from pathlib import Path
from typing import Optional, Generic, TypeVar

T = TypeVar("T")
"""The type of a configuration value"""


class EnvironmentVariable(Generic[T]):
    """Manages a configuration option using system environment variables"""

    def __init__(self, name, default=None, type_: T = str):
        self.name = name
        self.default = default
        self.type = type_

    def get(self) -> Optional[T]:
        value = os.environ.get(self.name, self.default)
        if value is None:
            return None
        return self.type(value)

    def is_set(self) -> bool:
        return self.name in os.environ


install_path = EnvironmentVariable(
    "BRAINFRAME_INSTALL_PATH",
    default="/usr/local/share/brainframe/",
    type_=Path,
)

data_path = EnvironmentVariable(
    "BRAINFRAME_DATA_PATH", default="/var/local/brainframe", type_=Path,
)

is_staging = EnvironmentVariable("BRAINFRAME_STAGING")
staging_username = EnvironmentVariable("BRAINFRAME_STAGING_USERNAME")
staging_password = EnvironmentVariable("BRAINFRAME_STAGING_PASSWORD")
