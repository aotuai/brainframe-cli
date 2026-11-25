from unittest import mock

import pytest
from brainframe.cli import dependencies
from brainframe.cli import os_utils


@pytest.mark.parametrize(
    "distro_id,expected", [("ubuntu", True), ("debian", False), ("", False)]
)
def test_supported_distribution(distro_id, expected):
    with mock.patch.object(os_utils.distro, "id", return_value=distro_id):
        assert os_utils.is_supported() is expected


def test_already_installed_dependency_does_not_need_supported_os():
    with mock.patch.object(
        dependencies.shutil, "which", return_value="/usr/bin/docker"
    ), mock.patch.object(os_utils, "is_supported", return_value=False):
        dependencies.docker.ensure(noninteractive=True, install_requested=True)
