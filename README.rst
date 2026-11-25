==============
BrainFrame CLI
==============

The BrainFrame CLI is a tool for installing and managing a BrainFrame server.

Installation
------------

The CLI is installable with Pip. Ubuntu 18.04 and 20.04 are officially
supported, but other versions of Linux are expected to work as well.

On Ubuntu:

.. code-block::

    sudo -H pip3 install brainframe-cli

Upgrading
---------

Pip can be used to upgrade to a new version.

.. code-block::

    sudo -H pip3 install --upgrade brainframe-cli

Usage
-----

To install BrainFrame, simply run the ``install`` command as root:

.. code-block::

    sudo brainframe install

BrainFrame can then be controlled like a normal Docker Compose application
using the ``compose`` command, which can be run from any directory.

.. code-block::

    brainframe compose up -d

The following will show logs,

.. code-block::

    brainframe compose logs -f core journal

How to integrate the following to cleanup logs,

.. code-block::

    sudo truncate -s 0 $(docker inspect --format='{{.LogPath}}' brainframe-core-1 brainframe-journal-1)

For more information, take a look at the `Getting Started guide`_.

.. _`Getting Started guide`: https://aotu.ai/docs/getting_started/

Contributing
------------

We happily take community contributions! If there's something you'd like to
work on, but you're not sure how to start, feel free to create an issue on
Github and we'll try to point you in the right direction.

We use a couple formatting tools to keep our code style consistent. If you get
any CI failures, you can run the following commands to automatically format
your code to fit our guidelines:

.. code-block:: bash

    pip install poetry==1.8.3
    poetry install
    poetry run isort .
    poetry run black .

Build one PyPI wheel for Python 3.6–3.12. The wheel records different
dependencies for older and newer Python versions:

.. code-block:: bash

    deployment/ide_cli build wheel-env
    deployment/ide_cli build wheel

To validate the wheel and intended destination without uploading, run
``deployment/ide_cli push wheel --dry-run``. After configuring a TestPyPI token
with ``TWINE_USERNAME`` and ``TWINE_PASSWORD`` or ``~/.pypirc``, run
``deployment/ide_cli push wheel``. Add ``--pypi`` to publish to production PyPI.

Build the PyInstaller standalone Linux executable separately:

.. code-block:: bash

    deployment/ide_cli build pyinstaller-binary-env
    deployment/ide_cli build pyinstaller-binary

This creates ``dist/brainframe``. To publish it to the dev releases bucket,
run ``deployment/ide_cli push pyinstaller-to-aws`` with an AWS profile and
region (pass ``--profile`` and, if needed, ``--region``). ``--profile`` selects
credentials; add ``--prod`` to select the production releases bucket. Run
``deployment/ide_cli push pyinstaller-to-aws --help`` for setup details.

Debian packages use ``build deb-env`` and ``build deb``. That build path is
currently not release-ready.

To remove generated wheels, the standalone executable, Debian packages, and
Debian staging files before a fresh build:

.. code-block:: bash

    deployment/ide_cli clean

``clean`` restores ``brainframe/cli/defaults.yaml`` if it still matches the
system-package copy left by a Debian build. It stops if that file has other
edits. Docker images remain cached; pass ``--no-cache`` to a ``*-env`` build when
testing the image build from scratch.

The wheel build uses one Python 3.12 Docker image and writes one wheel to
``dist/``. Install it for local testing with:

.. code-block:: bash

    pip install dist/brainframe_cli-0.3.3-py3-none-any.whl

Once the Docker environments exist, rerun ``build wheel`` or
``build pyinstaller-binary`` without rebuilding them.

