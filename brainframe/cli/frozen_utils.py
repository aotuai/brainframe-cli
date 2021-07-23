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
    if is_frozen():
        return _pyinstaller_tmp_path() / RELATIVE_DEFAULTS_FILE_PATH
    else:
        return _find_resource_location(RELATIVE_DEFAULTS_FILE_PATH)


def translations_path() -> Path:
    """
    :return: A path to the folder with the translation files
    :raises FileNotFoundError: If the defaults file is not present
    """
    if is_frozen():
        return _pyinstaller_tmp_path() / RELATIVE_TRANSLATIONS_PATH
    else:
        return _find_resource_location(RELATIVE_TRANSLATIONS_PATH)


def _find_resource_location(target: Path) -> Path:
    """Finds a resource given its path relative to the root of the project when the
    application is being run from source.

    :param target: The relative path of the resource from the root of the project
    :return: The absolute path to the resource
    """
    # Traverse up the file system from this file to find the root
    for parent in Path(__file__).absolute().parents:
        if (parent / target).exists():
            return parent / target

    raise FileNotFoundError()


def _pyinstaller_tmp_path() -> Path:
    # _MEIPASS is an attribute defined by PyInstaller at runtime
    return Path(sys._MEIPASS)  # type: ignore[attr-defined]
