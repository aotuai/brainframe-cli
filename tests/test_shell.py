from unittest import mock

from brainframe.cli import brainframe_shell


def test_shell_passes_path_and_sudo_user_as_arguments():
    with mock.patch.object(
        brainframe_shell, "assert_has_docker_permissions"
    ), mock.patch.object(
        brainframe_shell.os, "getcwd", return_value="/tmp/work space"
    ), mock.patch.object(
        brainframe_shell.os_utils, "_current_user", return_value="stephen"
    ), mock.patch.object(
        brainframe_shell.subprocess, "run"
    ) as run:
        brainframe_shell.run()

    command = run.call_args.args[0]
    assert command[command.index("-v") + 1] == "/tmp/work space:/host"
    assert command[command.index("-e") + 1] == "HOST_USER=stephen"
    assert run.call_args.kwargs == {"check": True}
