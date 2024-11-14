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

Build & install local build for test:

.. code-block:: bash
    poetry build
    pip install dist/brainframe_cli-0.3.0-py3-none-any.whl

Pyinstaller build:

The result will be in the dist/ directory
.. code-block:: bash
    pyinstaller package/main.spec

