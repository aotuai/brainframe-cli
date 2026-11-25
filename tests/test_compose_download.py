from unittest import mock

import pytest
from brainframe.cli import brainframe_compose


def test_failed_compose_replace_keeps_previous_file(tmp_path):
    target = tmp_path / "docker-compose.yml"
    target.write_text("previous")
    with mock.patch.object(
        brainframe_compose.os, "replace", side_effect=OSError("rename failed")
    ):
        with pytest.raises(OSError, match="rename failed"):
            brainframe_compose._replace_compose_file(target, "replacement")
    assert target.read_text() == "previous"
    assert list(tmp_path.glob(".brainframe-compose-*")) == []


def test_compose_replace_preserves_existing_mode(tmp_path):
    target = tmp_path / "docker-compose.yml"
    target.write_text("previous")
    target.chmod(0o664)
    brainframe_compose._replace_compose_file(target, "replacement")
    assert target.read_text() == "replacement"
    assert target.stat().st_mode & 0o777 == 0o664
