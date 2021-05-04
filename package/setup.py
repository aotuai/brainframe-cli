import subprocess

import setuptools

poetry_result = subprocess.run(
    ["poetry", "version"],
    check=True,
    stdout=subprocess.PIPE,
    encoding="utf-8",
)
poetry_output = poetry_result.stdout.strip()

name, version = poetry_output.split(" ")

setuptools.setup(
    name=name,
    version=version,
    packages=setuptools.find_namespace_packages(include="brainframe*",),
    scripts=["brainframe/cli/main.py"],
    package_data={
        "brainframe.cli.translations": ["*.yml"],
        "brainframe.cli": ["defaults.yaml"],
    },
    include_package_data=True,
)
