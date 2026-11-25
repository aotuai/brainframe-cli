"""Build one universal wheel with Python-specific dependency markers."""

import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    with tempfile.TemporaryDirectory(prefix="brainframe-wheel-") as build_dir:
        project = Path(build_dir)
        shutil.copytree(ROOT / "brainframe", project / "brainframe")
        shutil.copy2(ROOT / "README.rst", project / "README.rst")
        shutil.copy2(
            ROOT / "deployment" / "pyproject.toml.wheel",
            project / "pyproject.toml",
        )
        with (project / "pyproject.toml").open("a") as pyproject:
            pyproject.write(
                '\n[build-system]\nrequires = ["poetry-core==1.9.0"]\n'
                'build-backend = "poetry.core.masonry.api"\n'
            )
        output = ROOT / "dist"
        output.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "python",
                "-m",
                "build",
                "--wheel",
                "--no-isolation",
                "--outdir",
                str(output),
            ],
            cwd=project,
            check=True,
        )
        metadata = tomllib.loads((project / "pyproject.toml").read_text())
        version = metadata["tool"]["poetry"]["version"]
        wheel = output / "brainframe_cli-{}-py3-none-any.whl".format(version)
        if not wheel.is_file():
            raise RuntimeError("wheel build did not create {}".format(wheel))
        print("Built {}".format(wheel.name))


if __name__ == "__main__":
    main()
