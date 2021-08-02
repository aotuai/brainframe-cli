import sys
from pathlib import Path
from typing import Union


def is_frozen() -> bool:
    """
    :return: True if the application is running as a frozen executable
    """
    return getattr(sys, "frozen", False)


def _get_absolute_path(*args: Union[str, Path]) -> Path:
    """Gets the absolute path of a resource.

    :param args: Arguments to pass to the Path constructor
    :return: The absolute path of the resource
    """
    if is_frozen():
        path = Path(_pyinstaller_tmp_path(), *args)

        if not path.exists():
            raise RuntimeError(
                f"Missing resource in PyInstaller bundle: {args}"
            )

        return path
    else:
        for parent in Path(__file__).absolute().parents:
            path = Path(parent, *args)
            if path.exists():
                return path

        raise RuntimeError(
            f"Could not find the absolute path for resource: {args}"
        )


def _pyinstaller_tmp_path() -> Path:
    # _MEIPASS is an attribute defined by PyInstaller at runtime
    return Path(sys._MEIPASS)  # type: ignore[attr-defined]


RELATIVE_TRANSLATIONS_PATH = Path("brainframe/cli/translations")
TRANSLATIONS_PATH = _get_absolute_path(RELATIVE_TRANSLATIONS_PATH)
RELATIVE_DEFAULTS_FILE_PATH = Path("brainframe/cli/defaults.yaml")
DEFAULTS_FILE_PATH = _get_absolute_path(RELATIVE_DEFAULTS_FILE_PATH)
