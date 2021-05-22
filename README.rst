==============
BrainFrame CLI
==============

The BrainFrame CLI is a tool for installing and managing a BrainFrame server.

Installation
------------

The CLI is bundled into a single executable with PyInstaller for easy
installation. Ubuntu 18.04 and 20.04 are officially supported, but other
versions of Linux are expected to work as well.

.. code-block::

    sudo curl -o /usr/local/bin/brainframe -f -L "https://aotu.ai/releases/brainframe_cli/brainframe"
    sudo chmod +x /usr/local/bin/brainframe

Upgrading
---------

Just use the self-update command to update to the latest CLI release.

.. code-block::

    sudo brainframe self-update

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

    poetry run isort .
    poetry run black .

