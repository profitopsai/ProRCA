Installation
============

Getting ProRCA installed is straightforward using pip.

Install from PyPI
-----------------

The recommended way to install ProRCA is directly from the Python Package Index (PyPI):

.. code-block:: bash

   pip install profitops-rca

This command will download and install ProRCA along with all its required dependencies.

For Development
---------------

If you intend to contribute to ProRCA or want to install it directly from the source code after cloning the repository, you can install it with the optional development dependencies:

.. code-block:: bash

   # First, clone the repository (if you haven't already)
   git clone https://github.com/profitopsai/ProRCA.git
   cd ProRCA

   # Then install in editable mode with dev extras
   pip install -e .[dev]

This includes tools like ``pytest``, ``black``, and ``flake8`` needed for development and testing.