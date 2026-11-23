---
name: sphinx-1-docstring-style-guide
description: 'Sub-skill of sphinx: 1. Docstring Style Guide (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Docstring Style Guide (+3)

## 1. Docstring Style Guide


```python
# Use Google style (recommended)
def function(arg1: str, arg2: int = 10) -> bool:
    """
    Short description of function.

    Longer description that provides more detail about
    what the function does and how it works.

    Args:
        arg1: Description of arg1.
        arg2: Description of arg2. Defaults to 10.

    Returns:
        Description of return value.

    Raises:
        ValueError: If arg1 is empty.
        TypeError: If arg2 is not an integer.

    Example:
        >>> function("hello", 5)
        True

    Note:
        Additional notes about usage.

    See Also:
        related_function: Description of related function.
    """
    pass
```


## 2. Documentation Structure


```
docs/
├── source/
│   ├── _static/
│   │   ├── css/
│   │   │   └── custom.css
│   │   └── images/
│   ├── _templates/
│   │   └── layout.html
│   ├── api/
│   │   ├── index.rst
│   │   └── modules.rst
│   ├── guide/
│   │   ├── installation.rst
│   │   ├── quickstart.rst
│   │   └── advanced.rst
│   ├── tutorials/
│   │   └── basic.rst
│   ├── conf.py
│   ├── index.rst
│   └── changelog.rst
├── build/
├── Makefile
└── requirements.txt
```


## 3. Cross-Reference Best Practices


```rst
.. Use these reference styles

Classes and Methods
~~~~~~~~~~~~~~~~~~~

See :class:`mypackage.core.DataProcessor` for the main class.

Use :meth:`~mypackage.core.DataProcessor.process` method.

The :attr:`mypackage.core.DataProcessor.config` attribute.

Functions
~~~~~~~~~

Call :func:`mypackage.utils.helper` for utility functions.

Modules
~~~~~~~

Import from :mod:`mypackage.core` module.

External References
~~~~~~~~~~~~~~~~~~~

Uses :class:`numpy.ndarray` for array storage.

See :func:`pandas.read_csv` for file loading.
```


## 4. Version Documentation


```rst
.. Document version changes

API Changes
-----------

.. versionadded:: 1.2.0
   Added support for Parquet format.

.. versionchanged:: 1.3.0
   The ``format`` parameter now defaults to ``'auto'``.

.. deprecated:: 2.0.0
   Use :meth:`new_method` instead. Will be removed in v3.0.

.. versionremoved:: 2.0.0
   The ``old_param`` parameter has been removed.
```
