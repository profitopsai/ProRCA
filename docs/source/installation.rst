Installation
============

To get started with ProRCA, follow these steps to clone the repository and install the required dependencies.

Prerequisites
-------------

- Python 3.7 or higher
- Git
- pip (Python package manager)

Steps
-----

1. **Clone the Repository**

   Clone the ProRCA repository from GitHub:

   .. code-block:: bash

      git clone https://github.com/profitopsai/ProRCA.git
      cd ProRCA

2. **Install Dependencies**

   Install the package and its dependencies using pip:

   .. code-block:: bash

      pip install .

   This will install all required dependencies listed in ``pyproject.toml``, including:

   - dowhy
   - networkx
   - graphviz
   - adtk
   - matplotlib
   - seaborn
   - numpy
   - pandas

3. **Verify Installation**

   To confirm that ProRCA is installed correctly, run the following Python command:

   .. code-block:: python

      import prorca
      print(prorca.__version__)

   You should see the version number (e.g., ``0.1.0``).

Optional: Development Dependencies
----------------------------------

If you plan to contribute to ProRCA, you can install additional development dependencies:

.. code-block:: bash

   pip install .[dev]

This includes tools like ``pytest``, ``black``, and ``flake8`` for testing and linting.