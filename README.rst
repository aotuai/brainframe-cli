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
