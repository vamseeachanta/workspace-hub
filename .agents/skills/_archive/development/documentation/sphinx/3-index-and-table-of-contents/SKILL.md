---
name: sphinx-3-index-and-table-of-contents
description: 'Sub-skill of sphinx: 3. Index and Table of Contents.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 3. Index and Table of Contents

## 3. Index and Table of Contents


```rst
.. docs/source/index.rst

Welcome to MyProject
====================

MyProject is a powerful library for doing amazing things.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   configuration

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   guide/overview
   guide/core-concepts
   guide/advanced-usage
   guide/best-practices

.. toctree::
   :maxdepth: 3
   :caption: API Reference

   api/modules
   api/mypackage

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog
   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```
