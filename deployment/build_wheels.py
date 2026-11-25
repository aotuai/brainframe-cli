"""Build one universal wheel with Python-specific dependency markers."""

import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
def main():
    with tempfile.TemporaryDirectory(prefix="brainframe-wheel-") as build_dir:
        project = Path(build_dir)
        shutil.copytree(ROOT / "brainframe", project / "brainframe")
        shutil.copy2(ROOT / "README.rst", project / "README.rst")
        shutil.copy2(ROOT / "deployment" / "pyproject.toml.wheel", project / "pyproject.toml")
        with (project / "pyproject.toml").open("a") as pyproject:
            pyproject.write(
                '\n[build-system]\nrequires = ["poetry-core==1.9.0"]\n'
                'build-backend = "poetry.core.masonry.api"\n'
            )
        output = ROOT / "dist"
        output.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["python", "-m", "build", "--wheel", "--no-isolation", "--outdir", str(output)],
            cwd=project,
            check=True,
        )
        print("Built {}".format(", ".join(p.name for p in output.glob("*.whl"))))


if __name__ == "__main__":
    main()
