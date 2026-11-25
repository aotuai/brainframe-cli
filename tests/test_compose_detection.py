import importlib
import subprocess
import unittest
from unittest import mock

from brainframe.cli import brainframe_compose
from brainframe.cli.commands.utils import by_name

install_mod = importlib.import_module("brainframe.cli.commands.install")


class ComposeDetectionTests(unittest.TestCase):
    def test_prefers_docker_compose_plugin(self):
        with mock.patch.object(
            brainframe_compose.subprocess,
            "check_output",
            return_value=b"2.39.0",
        ) as check_output:
            command, version = brainframe_compose.get_docker_compose_command()

        self.assertEqual(command, ["docker", "compose"])
        self.assertEqual(version, b"2.39.0")
        check_output.assert_called_once_with(
            ["docker", "compose", "version", "--short"],
            stderr=subprocess.DEVNULL,
        )

    def test_falls_back_to_docker_compose_command(self):
        with mock.patch.object(
            brainframe_compose.subprocess,
            "check_output",
            side_effect=[FileNotFoundError(), b"1.29.2"],
        ):
            command, version = brainframe_compose.get_docker_compose_command()

        self.assertEqual(command, ["docker-compose"])
        self.assertEqual(version, b"1.29.2")

    def test_reports_missing_compose(self):
        with mock.patch.object(
            brainframe_compose.subprocess,
            "check_output",
            side_effect=FileNotFoundError(),
        ), mock.patch.object(
            brainframe_compose.print_utils,
            "fail_translate",
            side_effect=RuntimeError("missing Compose"),
        ) as fail:
            with self.assertRaisesRegex(RuntimeError, "missing Compose"):
                brainframe_compose.get_docker_compose_command()

        fail.assert_called_once_with(
            "install.install-dependency-manually", dependency="Docker Compose"
        )

    def test_reports_compose_command_failure(self):
        with mock.patch.object(
            brainframe_compose.subprocess,
            "check_output",
            side_effect=[
                subprocess.CalledProcessError(1, ["docker", "compose"]),
                FileNotFoundError(),
            ],
        ), mock.patch.object(
            brainframe_compose.print_utils,
            "fail_translate",
            side_effect=RuntimeError("compose failed"),
        ) as fail:
            with self.assertRaisesRegex(RuntimeError, "compose failed"):
                brainframe_compose.get_docker_compose_command()
        self.assertEqual(
            fail.call_args.args[0], "install.compose-command-failed"
        )

    def test_frozen_installer_checks_available_compose(self):
        args = mock.Mock(noninteractive=True, install_docker=False)
        with mock.patch.object(
            install_mod.os_utils, "is_root", return_value=True
        ), mock.patch.object(
            install_mod.os_utils, "is_supported", return_value=True
        ), mock.patch.object(
            install_mod, "_parse_args", return_value=args
        ), mock.patch.object(
            install_mod.dependencies.docker, "ensure"
        ), mock.patch.object(
            install_mod.frozen_utils, "is_frozen", return_value=True
        ), mock.patch.object(
            install_mod.brainframe_compose,
            "get_docker_compose_command",
            side_effect=RuntimeError("checked Compose"),
        ) as check:
            with self.assertRaisesRegex(RuntimeError, "checked Compose"):
                by_name["install"]()

        check.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
