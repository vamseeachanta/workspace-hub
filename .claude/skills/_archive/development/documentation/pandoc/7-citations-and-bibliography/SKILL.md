---
name: pandoc-7-citations-and-bibliography
description: 'Sub-skill of pandoc: 7. Citations and Bibliography (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 7. Citations and Bibliography (+1)

## 7. Citations and Bibliography


```bibtex
%% references.bib
@article{smith2024,
    author = {Smith, John and Doe, Jane},
    title = {Advanced Documentation Techniques},
    journal = {Journal of Technical Writing},
    year = {2024},
    volume = {15},
    number = {3},
    pages = {42--58},
    doi = {10.1234/jtw.2024.001}
}

@book{johnson2023,
    author = {Johnson, Robert},
    title = {The Complete Guide to Markdown},
    publisher = {Tech Press},
    year = {2023},
    address = {New York},
    isbn = {978-0-123456-78-9}
}

@inproceedings{williams2025,
    author = {Williams, Sarah},
    title = {Document Automation Best Practices},
    booktitle = {Proceedings of DocCon 2025},
    year = {2025},
    pages = {100--115},
    organization = {Documentation Society}
}

@online{pandocmanual,
    author = {{Pandoc Contributors}},
    title = {Pandoc User's Guide},
    year = {2024},
    url = {https://pandoc.org/MANUAL.html},
    urldate = {2024-01-15}
}
```

```markdown
<!-- document.md with citations -->
---
title: "Research Paper"
bibliography: references.bib
csl: apa.csl
---

# Literature Review

According to @smith2024, documentation is essential for
project success. This aligns with earlier findings
[@johnson2023; @williams2025].

The standard approach uses markdown formatting
[see @pandocmanual, chapter 3].

Multiple citations can be grouped together
[@smith2024; @johnson2023, pp. 15-20].

# References

::: {#refs}
:::
```

```bash
# Generate PDF with citations
pandoc document.md -o document.pdf \
    --citeproc \
    --bibliography=references.bib \
    --csl=apa.csl \
    --pdf-engine=xelatex

# Download CSL styles
# https://github.com/citation-style-language/styles
curl -O https://raw.githubusercontent.com/citation-style-language/styles/master/apa.csl
curl -O https://raw.githubusercontent.com/citation-style-language/styles/master/ieee.csl
curl -O https://raw.githubusercontent.com/citation-style-language/styles/master/chicago-author-date.csl
```


## 8. Cross-References with pandoc-crossref


```bash
# Install pandoc-crossref
# macOS
brew install pandoc-crossref

# Or download from releases
# https://github.com/lierdakil/pandoc-crossref/releases
```

```markdown
<!-- document.md with cross-references -->
---
title: "Document with Cross-References"
---

# Introduction

See @fig:architecture for the system overview.
The data flow is described in @sec:dataflow.
Results are shown in @tbl:results.
The equation @eq:formula describes the relationship.

# System Architecture {#sec:architecture}

![System Architecture Diagram](images/architecture.png){#fig:architecture}

# Data Flow {#sec:dataflow}

The process follows these steps...

# Results

| Metric | Value | Unit |
|--------|-------|------|
| Speed  | 100   | ms   |
| Memory | 256   | MB   |

: Performance metrics {#tbl:results}

# Mathematical Model

The core formula is:

$$ E = mc^2 $$ {#eq:formula}

Equation @eq:formula shows Einstein's famous equation.
```

```bash
# Generate PDF with cross-references
pandoc document.md -o document.pdf \
    --filter pandoc-crossref \
    --citeproc \
    --pdf-engine=xelatex \
    --number-sections

# pandoc-crossref options in YAML
# ---
# figureTitle: "Figure"
# tableTitle: "Table"
# listingTitle: "Listing"
# figPrefix: "Fig."
# tblPrefix: "Table"
# eqnPrefix: "Eq."
# secPrefix: "Section"
# ---
```
