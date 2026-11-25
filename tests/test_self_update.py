import hashlib
import importlib
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

self_update_mod = importlib.import_module(
    "brainframe.cli.commands.self_update"
)


class SelfUpdateTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.executable = Path(self.directory.name) / "brainframe"
        self.executable.write_bytes(b"old executable")
        self.executable.chmod(0o750)

    def assert_no_temporary_files(self):
        self.assertEqual(
            list(Path(self.directory.name).glob(".brainframe-update-*")), []
        )

    def test_replacement_preserves_executable_mode(self):
        self_update_mod._replace_executable(
            self.executable, [b"\x7fELFnew ", b"executable"]
        )

        self.assertEqual(
            self.executable.read_bytes(), b"\x7fELFnew executable"
        )
        self.assertEqual(stat.S_IMODE(self.executable.stat().st_mode), 0o750)
        self.assert_no_temporary_files()

    def test_interrupted_download_leaves_original_intact(self):
        def interrupted_blocks():
            yield b"\x7fELFpartial replacement"
            raise OSError("download interrupted")

        with self.assertRaisesRegex(OSError, "download interrupted"):
            self_update_mod._replace_executable(
                self.executable, interrupted_blocks()
            )

        self.assertEqual(self.executable.read_bytes(), b"old executable")
        self.assertEqual(stat.S_IMODE(self.executable.stat().st_mode), 0o750)
        self.assert_no_temporary_files()

    def test_failed_replace_leaves_original_intact(self):
        with mock.patch.object(
            self_update_mod.os, "replace", side_effect=OSError("rename failed")
        ):
            with self.assertRaisesRegex(OSError, "rename failed"):
                self_update_mod._replace_executable(
                    self.executable, [b"\x7fELFnew"]
                )

        self.assertEqual(self.executable.read_bytes(), b"old executable")
        self.assert_no_temporary_files()

    def test_rejects_html_response(self):
        with self.assertRaisesRegex(ValueError, "ELF"):
            self_update_mod._replace_executable(
                self.executable, [b"<html>portal"]
            )
        self.assertEqual(self.executable.read_bytes(), b"old executable")
        self.assert_no_temporary_files()

    def test_rejects_truncated_response(self):
        with self.assertRaisesRegex(ValueError, "size"):
            self_update_mod._replace_executable(
                self.executable, [b"\x7fELFpartial"], expected_size=100
            )
        self.assertEqual(self.executable.read_bytes(), b"old executable")
        self.assert_no_temporary_files()

    def test_rejects_wrong_checksum(self):
        with self.assertRaisesRegex(ValueError, "checksum"):
            self_update_mod._replace_executable(
                self.executable,
                [b"\x7fELFpayload"],
                expected_sha256=hashlib.sha256(b"different").hexdigest(),
            )
        self.assertEqual(self.executable.read_bytes(), b"old executable")
        self.assert_no_temporary_files()

    def test_accepts_matching_size_and_checksum(self):
        payload = b"\x7fELFpayload"
        self_update_mod._replace_executable(
            self.executable,
            [payload],
            expected_size=len(payload),
            expected_sha256=hashlib.sha256(payload).hexdigest(),
        )
        self.assertEqual(self.executable.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
