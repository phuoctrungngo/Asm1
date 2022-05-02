# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/stable/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("."))


# -- Project information -----------------------------------------------------

project = "OpenFF Evaluator"
copyright = "2019, Open Force Field Consortium."
author = "Open Force Field Consortium"

# The short X.Y version
version = ""
# The full version, including alpha/beta/rc tags
release = ""


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinxcontrib.bibtex",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.doctest",
    "sphinx.ext.todo",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "nbsphinx",
    "openff_sphinx_theme",
]

# Autodoc settings
autosummary_generate = True
autodoc_preserve_defaults = True
autodoc_typehints_format = "short"
# Workaround for autodoc_typehints_format not working for attributes
# see https://github.com/sphinx-doc/sphinx/issues/10290#issuecomment-1079740009
python_use_unqualified_type_names = True

autodoc_default_options = {
    "members": True,
    "inherited-members": True,
    "member-order": "bysource",
}

autodoc_mock_imports = [
    "dask",
    "dask_jobqueue",
    "distributed",
    "packmol",
    "pydantic",
    "pymbar",
    "scipy",
    "openmm",
    "typing_extensions",
    "yaml",
]

# Autolabel settings
autosectionlabel_maxdepth = 3
autosectionlabel_prefix_document = True

suppress_warnings = [
    "autosectionlabel.releasehistory",
]

# nbsphinx settings
nbsphinx_execute = "never"

# sphinx bibtext settings
bibtex_bibfiles = [
    os.path.join("properties", "commonworkflows.bib"),
    os.path.join("properties", "gradients.bib"),
    os.path.join("properties", "properties.bib"),
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = [".rst"]
# source_suffix = '.rst'

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# Set up the intershinx mappings.
intersphinx_mapping = {
    "python": ("https://docs.python.org/", None),
    "numpy": ("https://docs.scipy.org/doc/numpy/", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "mdtraj": ("http://mdtraj.org/latest/", None),
    "dask": ("http://docs.dask.org/en/latest/", None),
    "dask.distributed": ("https://distributed.dask.org/en/latest/", None),
    "distributed": ("https://distributed.dask.org/en/latest/", None),
    "dask_jobqueue": ("https://jobqueue.dask.org/en/latest/", None),
    "openff.toolkit": (
        "https://open-forcefield-toolkit.readthedocs.io/en/latest/",
        None,
    ),
    "pint": ("https://pint.readthedocs.io/en/latest/", None),
}

# Set up mathjax.
mathjax_path = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"

# -- Options for HTML output -------------------------------------------------

html_theme = "openff_sphinx_theme"
html_sidebars = {"**": ["globaltoc.html", "localtoc.html", "searchbox.html"]}

html_theme_options = {
    # Repository integration
    # Set the repo url for the link to appear
    "repo_url": "https://github.com/openforcefield/openff-evaluator",
    # The name of the repo. If must be set if repo_url is set
    "repo_name": "openff-evaluator",
    # Must be one of github, gitlab or bitbucket
    "repo_type": "github",
    # Colour for sidebar captions and other accents. One of
    # openff-blue, openff-toolkit-blue, openff-dataset-yellow,
    # openff-evaluator-orange, aquamarine, lilac, amaranth, grape,
    # violet, pink, pale-green, green, crimson, eggplant, turquoise,
    # or a tuple of three ints in the range [0, 255] corresponding to
    # a position in RGB space.
    "color_accent": "openff-evaluator-orange",
}

html_static_path = ["_static"]

# sphinx-notfound-page
# https://github.com/readthedocs/sphinx-notfound-page
# Renders a 404 page with absolute links
from importlib.util import find_spec as find_import_spec

if find_import_spec("notfound"):
    extensions.append("notfound.extension")

    notfound_urls_prefix = "/projects/evaluator/en/stable/"
    notfound_context = {
        "title": "404: File Not Found",
        "body": f"""
    <h1>404: File Not Found</h1>
    <p>
        Sorry, we couldn't find that page. This often happens as a result of
        following an outdated link. Please check the
        <a href="{notfound_urls_prefix}">latest stable version</a>
        of the docs, unless you're sure you want an earlier version, and
        try using the search box or the navigation menu on the left.
    </p>
    <p>
    </p>
    """,
    }


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "evaluatordoc"


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "evaluator.tex",
        "OpenFF Evaluator Documentation",
        "openff-evaluator",
        "manual",
    ),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, "openff-evaluator", "OpenFF Evaluator Documentation", [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "openff-evaluator",
        "OpenFF Evaluator Documentation",
        author,
        "openff-evaluator",
        "A physical property evaluation toolkit from the Open Forcefield Consortium.",
        "Miscellaneous",
    ),
]


# -- Extension configuration -------------------------------------------------
