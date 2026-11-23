---
name: sphinx-1-project-initialization
description: 'Sub-skill of sphinx: 1. Project Initialization (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Project Initialization (+1)

## 1. Project Initialization


```bash
# Quick start with sphinx-quickstart
sphinx-quickstart docs

# Answer the prompts:
# > Separate source and build directories (y/n) [n]: y
# > Project name: MyProject
# > Author name(s): Your Name
# > Project release: 1.0.0
# > Project language [en]: en

# Generated structure:
# docs/
# ├── source/
# │   ├── conf.py
# │   ├── index.rst
# │   └── _static/
# │   └── _templates/
# └── build/
#     └── (output files)

# Or manual setup
mkdir -p docs/source docs/build
touch docs/source/conf.py docs/source/index.rst
```


## 2. Basic Configuration (conf.py)


```python
# docs/source/conf.py

# -- Project information -----------------------------------------------------
project = 'MyProject'
copyright = '2024-2026, Your Name'
author = 'Your Name'
release = '1.0.0'
version = '1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.githubpages',
    'sphinx_rtd_theme',
    'sphinx_copybutton',
    'myst_parser',
]

# Source file suffixes
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# Master document
master_doc = 'index'

# Exclude patterns
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Pygments style
pygments_style = 'sphinx'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = '_static/logo.png'
html_favicon = '_static/favicon.ico'

html_theme_options = {
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
}

# -- Options for autodoc -----------------------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
}

autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'
autodoc_class_signature = 'separated'

# -- Options for Napoleon (Google/NumPy docstrings) -------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
napoleon_attr_annotations = True

# -- Options for intersphinx -------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
}

# -- Options for todo extension ----------------------------------------------
todo_include_todos = True

# -- Options for LaTeX/PDF output --------------------------------------------
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '11pt',
    'preamble': r'''
        \usepackage{charter}
        \usepackage[defaultsans]{lato}
        \usepackage{inconsolata}
    ''',
}

latex_documents = [
    (master_doc, 'MyProject.tex', 'MyProject Documentation',
     'Your Name', 'manual'),
]

# -- Options for EPUB output -------------------------------------------------
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright
epub_exclude_files = ['search.html']
```
