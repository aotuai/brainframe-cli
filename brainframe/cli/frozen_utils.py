import sys
from pathlib import Path


def is_frozen() -> bool:
    """
    :return: True if the application is running as a frozen executable
    """
    return getattr(sys, "frozen", False)


RELATIVE_TRANSLATIONS_PATH = Path("brainframe/cli/translations")
RELATIVE_DEFAULTS_FILE_PATH = Path("brainframe/cli/defaults.yaml")


def defaults_file_path() -> Path:
    """
    :return: A path to the included defaults file
    :raises FileNotFoundError: If the defaults file is not present
    """
    return _get_resource_absolute_path(RELATIVE_DEFAULTS_FILE_PATH)


def translations_path() -> Path:
    """
    :return: A path to the folder with the translation files
    :raises FileNotFoundError: If the defaults file is not present
    """
    return _get_resource_absolute_path(RELATIVE_TRANSLATIONS_PATH)


def _get_resource_absolute_path(target: Path) -> Path:
    """Gets the absolute path of a resource.

    :param target: The relative path of the resource from the root of the project
    :return: The absolute path of the resource
    :raises FileNotFoundError: If the resource cannot be found
    """
    if is_frozen():
        path = _pyinstaller_tmp_path() / target
        if not path.is_file():
            raise FileNotFoundError()
        return path
    else:
        for parent in Path(__file__).absolute().parents:
            if (parent / target).exists():
                return parent / target

        raise FileNotFoundError()


def _pyinstaller_tmp_path() -> Path:
    # _MEIPASS is an attribute defined by PyInstaller at runtime
    return Path(sys._MEIPASS)  # type: ignore[attr-defined]
