import sys
from pathlib import Path


def is_frozen() -> bool:
    """
    :return: True if the application is running as a frozen executable
    """
    return getattr(sys, "frozen", False)


RELATIVE_TRANSLATIONS_PATH = Path("brainframe/cli/translations")


def translations_path() -> Path:
    """
    :return: A path to the folder with the translation files
    """
    if is_frozen():
        return getattr(sys, "_MEIPASS") / RELATIVE_TRANSLATIONS_PATH
    else:
        # The application is running from source
        # Traverse up the file system from this file to find the root
        for parent in Path(__file__).absolute().parents:
            if (parent / RELATIVE_TRANSLATIONS_PATH).is_dir():
                return parent / RELATIVE_TRANSLATIONS_PATH

        raise RuntimeError(
            f"Unable to find the translations path! Started "
            f"looking at: '{Path(__file__).absolute()}'"
        )
