from unittest import mock

import pytest
from brainframe.cli import brainframe_compose


def test_latest_version_strips_whitespace():
    response = mock.Mock(ok=True, text="  v1.2.3\n")
    with mock.patch.object(
        brainframe_compose.requests, "get", return_value=response
    ):
        assert brainframe_compose.get_latest_version() == "v1.2.3"


@pytest.mark.parametrize("tag", ["v0.32.3", "v0.32.3.1", "v1.2.3rc1"])
def test_latest_version_accepts_any_valid_version(tag):
    response = mock.Mock(ok=True, text=tag + "\n")
    with mock.patch.object(
        brainframe_compose.requests, "get", return_value=response
    ):
        assert brainframe_compose.get_latest_version() == tag


@pytest.mark.parametrize(
    "response",
    [
        mock.Mock(ok=False, status_code=503),
        mock.Mock(ok=True, text="<html>portal</html>"),
    ],
)
def test_latest_version_rejects_bad_response(response):
    with mock.patch.object(
        brainframe_compose.requests, "get", return_value=response
    ), mock.patch.object(
        brainframe_compose.print_utils,
        "fail_translate",
        side_effect=RuntimeError("bad version"),
    ):
        with pytest.raises(RuntimeError, match="bad version"):
            brainframe_compose.get_latest_version()
