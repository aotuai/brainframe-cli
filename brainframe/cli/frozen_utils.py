import sys
from pathlib import Path


def is_frozen() -> bool:
    """
    :return: True if the application is running as a frozen executable
    """
    return getattr(sys, "frozen", False)


RELATIVE_TRANSLATIONS_PATH = Path("brainframe/cli/translations")
RELATIVE_DEFAULTS_FILE_PATH = Path("brainframe/cli/defaults.yaml")


class ResourceNotFoundError(Exception):
    pass


def defaults_file_path() -> Path:
    """
    :return: A path to the included defaults file
    """
    if is_frozen():
        return getattr(sys, "_MEIPASS") / RELATIVE_DEFAULTS_FILE_PATH
    else:
        return _find_resource_location(RELATIVE_DEFAULTS_FILE_PATH)


def translations_path() -> Path:
    """
    :return: A path to the folder with the translation files
    """
    if is_frozen():
        return getattr(sys, "_MEIPASS") / RELATIVE_TRANSLATIONS_PATH
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

    raise ResourceNotFoundError()
