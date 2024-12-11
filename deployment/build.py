import argparse
import itertools
import os
import shutil
import subprocess
import sys
from pathlib import Path

from parse_wheel import parse_wheel

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent


def get_py_tag(version):
    try:
        major, minor = version.split(".")[:2]
    except Exception as e:
        print(f"Version '{version}' format error: {e}")
        sys.exit(1)
    return f"py{major}{minor}"


def find_matching_file(filename, py_tags):
    for l in range(len(py_tags), 0, -1):
        for combo in itertools.combinations(py_tags, l):
            candidate = f"{filename}.{'.'.join(combo)}"
            if (SCRIPT_DIR / candidate).exists():
                return candidate, True
    return candidate, False


def copy_project_files(versions):
    py_tags = [get_py_tag(v) for v in versions]

    toml_file, toml_found = find_matching_file("pyproject.toml", py_tags)
    lock_file, lock_found = find_matching_file("poetry.lock", py_tags)

    if not toml_found or not lock_found:
        print(f"Error: Could not find {toml_file}, {lock_file}")
        sys.exit(1)

    shutil.copy(SCRIPT_DIR / toml_file, PROJECT_ROOT / "pyproject.toml")
    shutil.copy(SCRIPT_DIR / lock_file, PROJECT_ROOT / "poetry.lock")
    print(f"Copied {toml_file}, {lock_file}")

    return py_tags


# PEP 427 https://peps.python.org/pep-0427/
# {distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.whl


def build_wheel(py_tags, python_version):
    try:
        env = os.environ.copy()
        env["PYTHON_VERSION"] = python_version
        print(f"Setting PYTHON_VERSION to {python_version}")

        subprocess.run(
            ["poetry", "build", "-f", "wheel"],
            check=True,
            cwd=PROJECT_ROOT,
            env=env,
        )

        dist_dir = PROJECT_ROOT / "dist"
        for wheel_file in dist_dir.glob("*.whl"):
            parse_wheel(dist_dir / wheel_file)
    except subprocess.CalledProcessError as e:
        print(f"Error building wheel: {e}")
        sys.exit(1)


def clean():
    dist_dir = PROJECT_ROOT / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print("Removed dist directory")

    pyproject_file = PROJECT_ROOT / "pyproject.toml"
    if pyproject_file.exists():
        pyproject_file.unlink()
        print("Removed pyproject.toml")

    lock_file = PROJECT_ROOT / "poetry.lock"
    if lock_file.exists():
        lock_file.unlink()
        print("Removed poetry.lock")


def main():
    parser = argparse.ArgumentParser(
        description="Build Python wheels or clean project"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean the project (remove dist directory, pyproject.toml, and poetry.lock)",
    )
    parser.add_argument(
        "--versions",
        nargs="+",
        default=["3.8"],
        help="Python version(s) to build for (default: 3.8)",
    )
    parser.add_argument(
        "--copy-only",
        action="store_true",
        help="Only copy pyproject.toml, and poetry.lock",
    )

    args = parser.parse_args()

    if args.clean:
        clean()
    elif args.copy_only:
        py_tags = copy_project_files(args.versions)
    else:
        print(f"Build for Python Versions: {', '.join(args.versions)}")
        py_tags = copy_project_files(args.versions)
        python_version = ".".join(args.versions[0].split(".")[:2])
        build_wheel(py_tags, python_version)


if __name__ == "__main__":
    main()
