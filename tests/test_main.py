from unittest import mock

import pytest
from brainframe.cli import __version__
from brainframe.cli import main


def test_version_option_exits_successfully(capsys):
    with mock.patch.object(
        main.sys, "argv", ["brainframe", "--version"]
    ), mock.patch.object(main.config, "load"):
        with pytest.raises(SystemExit) as error:
            main.main()
    assert error.value.code == 0
    assert __version__ in capsys.readouterr().out


@pytest.mark.parametrize("arguments", [[], ["unknown-command"]])
def test_missing_or_unknown_command_fails(arguments):
    with mock.patch.object(
        main.sys, "argv", ["brainframe"] + arguments
    ), mock.patch.object(main.config, "load"):
        with pytest.raises(SystemExit) as error:
            main.main()
    assert error.value.code == 2
