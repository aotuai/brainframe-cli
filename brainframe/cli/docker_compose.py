from pathlib import Path
from typing import List
import shutil

from . import os_utils


BRAINFRAME_DOCKER_COMPOSE_URL = (
    "https://aotu.ai/releases/brainframe/{version}/docker-compose.yml"
)


def run(install_path: Path, commands: List[str]):
    compose_path = install_path / "docker-compose.yml"

    full_command = ["docker-compose", "-f", str(compose_path)]

    # Provide the override file if it exists
    compose_override_path = install_path / "docker-compose.override.yml"
    if compose_override_path.is_file():
        full_command += ["-f", str(compose_override_path)]

    os_utils.run(full_command + commands)


def download(target: Path, version):
    # Run the download as root if we're not in the BrainFrame group
    run_as_root = not os_utils.is_in_group("brainframe")

    url = BRAINFRAME_DOCKER_COMPOSE_URL.format(version=version)
    os_utils.run(
        ["curl", "-o", str(target), "--fail", "--location", url],
        root=run_as_root,
    )

    if run_as_root:
        # Fix up the permissions if we ran as root
        os_utils.run(["chgrp", "brainframe", str(target)])
