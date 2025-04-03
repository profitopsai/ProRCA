# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",  # Optional for Markdown support
]


html_theme = "sphinx_book_theme"

project = "ProRCA"
copyright = "2025, Ahmed Dawoud"
author = "Ahmed Dawoud"
release = "0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_static_path = ["_static"]


html_theme_options = {
    "repository_url": "https://github.com/profitopsai/ProRCA",
    "use_repository_button": True,
    "primary_color": "#1e3a8a",  # A blue from the ProRCA logo
}
