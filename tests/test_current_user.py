from unittest import mock

from brainframe.cli import os_utils


def test_sudo_user_works_without_logname():
    with mock.patch.dict(
        os_utils.os.environ, {"SUDO_USER": "stephen"}, clear=True
    ):
        assert os_utils._current_user() == "stephen"


def test_user_falls_back_without_login_environment():
    with mock.patch.dict(
        os_utils.os.environ, {}, clear=True
    ), mock.patch.object(os_utils.getpass, "getuser", return_value="stephen"):
        assert os_utils._current_user() == "stephen"
