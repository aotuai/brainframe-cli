import os
import readline
import sys
from enum import Enum
from pathlib import Path
from typing import NoReturn

import i18n


class Color(Enum):
    """ANSI escape codes representing colors in the terminal theme."""

    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# These delimiters tell GNU readline that any characters between them are
# non-visible. These should be put before and after ASCII escape codes. Without
# these, escape codes mess up readline's text wrapping support.
# See: https://superuser.com/a/301355
_NON_VISIBLE_START = "\001"
_NON_VISIBLE_END = "\002"


def ask_yes_no(message_id, **kwargs) -> bool:
    """Prompts the user with a yes or no question. The default value is yes.

    :param message_id: The ID of the question to print
    :return: The user's choice
    """
    while True:
        question = i18n.t(message_id, **kwargs)
        choice = input_color(f"{question} [Y/n] ", Color.BLUE)
        choice = choice.strip().lower()
        if choice not in ["y", "n", ""]:
            translate("general.invalid-yes-no-input")
            continue

        print()

        return choice in ["y", ""]


def ask_path(message_id, default: Path) -> Path:
    message = i18n.t(message_id) + "\n"
    message += f"[{i18n.t('general.default')}: {default}] "
    choice = input_color(message, Color.BLUE)

    print()

    if len(choice.strip()) == 0:
        return default

    return Path(choice)


def art() -> None:
    print_color(_BRAINFRAME_ART, Color.MAGENTA)


def translate(message_id, color=Color.END, **kwargs):
    print_color(i18n.t(message_id, **kwargs), color)


def warning_translate(message_id, color=Color.YELLOW, **kwargs):
    print_color(i18n.t(message_id, **kwargs), color)


def fail_translate(message_id, **kwargs) -> NoReturn:
    fail(i18n.t(message_id, **kwargs))


def fail(message, **kwargs) -> NoReturn:
    print_color(message, Color.RED, file=sys.stderr, **kwargs)
    sys.exit(1)


def print_color(message, color: Color, **kwargs) -> None:
    color = _check_no_color(color)
    print(f"{color.value}{message}{Color.END.value}", **kwargs)


def input_color(message, color: Color) -> str:
    color = _check_no_color(color)
    # See https://superuser.com/a/301355 for why these non-visible delimiters
    # are necessary for input()
    return input(
        f"{_NON_VISIBLE_START}{color.value}{_NON_VISIBLE_END}"
        f"{message}"
        f"{_NON_VISIBLE_START}{Color.END.value}{_NON_VISIBLE_END}"
    )


def _check_no_color(color: Color) -> Color:
    """Turns off color if the user wants.
    See: https://no-color.org/
    """
    if "NO_COLOR" in os.environ:
        return Color.END
    return color


_DOCKER_COMPOSE_DOWNLOAD_URL = (
    "https://github.com/docker/compose/releases/download/1.25.5/"
    "docker-compose-Linux-x86_64"
)

_BRAINFRAME_ART = r"""
 _______            __       _______
|   _   .----.---.-|__.-----|   _   .----.---.-.--------.-----.
|.  1   |   _|  _  |  |     |.  1___|   _|  _  |        |  -__|
|.  _   |__| |___._|__|__|__|.  __) |__| |___._|__|__|__|_____|
|:  1    \                  |:  |
|::.. .  /                  |::.|
`-------'                   `---'
                                        Installer

"""

# Importing readline has the side-effect of augmenting the `input` function
# with GNU readline features.
_ = readline
