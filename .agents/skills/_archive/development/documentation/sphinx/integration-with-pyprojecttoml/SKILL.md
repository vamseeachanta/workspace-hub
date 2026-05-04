---
name: sphinx-integration-with-pyprojecttoml
description: 'Sub-skill of sphinx: Integration with pyproject.toml (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Integration with pyproject.toml (+2)

## Integration with pyproject.toml


```toml
# pyproject.toml
[project]
name = "mypackage"
version = "1.0.0"
description = "A Python package with Sphinx docs"
readme = "README.md"
requires-python = ">=3.8"

[project.optional-dependencies]
docs = [
    "sphinx>=7.0.0",
    "sphinx-rtd-theme>=2.0.0",
    "sphinx-autodoc-typehints>=1.25.0",
    "sphinx-copybutton>=0.5.0",
    "myst-parser>=2.0.0",
]

[tool.setuptools.packages.find]
where = ["src"]
```


## Integration with Makefile


```makefile
# docs/Makefile
SPHINXOPTS    ?= -W --keep-going
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

.PHONY: help clean html pdf epub linkcheck livehtml

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

clean:
	rm -rf $(BUILDDIR)/*

html:
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)
	@echo "Build finished. Open $(BUILDDIR)/html/index.html"

pdf:
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex" $(SPHINXOPTS)
	@$(MAKE) -C "$(BUILDDIR)/latex" all-pdf
	@echo "Build finished. PDF at $(BUILDDIR)/latex/*.pdf"

epub:
	@$(SPHINXBUILD) -b epub "$(SOURCEDIR)" "$(BUILDDIR)/epub" $(SPHINXOPTS)
	@echo "Build finished. EPUB at $(BUILDDIR)/epub/*.epub"

linkcheck:
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" $(SPHINXOPTS)

livehtml:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)
```


## Integration with Pre-commit


```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: sphinx-build
        name: Build Sphinx documentation
        entry: sphinx-build -b html docs/source docs/build/html -W
        language: system
        pass_filenames: false
        types: [python, rst, markdown]
```
