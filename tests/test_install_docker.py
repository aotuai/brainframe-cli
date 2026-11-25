from unittest import mock

import pytest
from brainframe.cli import dependencies


def test_failed_docker_script_is_never_executed():
    response = mock.Mock(ok=False, status_code=503, text="error")
    with mock.patch.object(
        dependencies.requests, "get", return_value=response
    ), mock.patch.object(
        dependencies.print_utils,
        "fail_translate",
        side_effect=RuntimeError("download failed"),
    ), mock.patch.object(
        dependencies.os_utils, "run"
    ) as run:
        with pytest.raises(RuntimeError, match="download failed"):
            dependencies._install_docker()
    run.assert_not_called()
