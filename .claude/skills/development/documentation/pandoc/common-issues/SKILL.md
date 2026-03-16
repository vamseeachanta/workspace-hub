---
name: pandoc-common-issues
description: 'Sub-skill of pandoc: Common Issues (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Common Issues (+1)

## Common Issues


#### PDF Engine Not Found

```bash
# Check if xelatex is installed
which xelatex

# Install on Ubuntu
sudo apt-get install texlive-xetex

# Use pdflatex instead
pandoc doc.md -o doc.pdf --pdf-engine=pdflatex
```

#### Missing LaTeX Packages

```bash
# Install specific package (TeX Live)
tlmgr install <package-name>

# Install common packages
sudo apt-get install texlive-latex-extra texlive-fonts-extra

# Check which package provides a file
tlmgr search --file <filename>
```

#### Unicode Characters in PDF

```bash
# Use XeLaTeX for Unicode support
pandoc doc.md -o doc.pdf \
    --pdf-engine=xelatex \
    -V mainfont="DejaVu Sans"
```

#### Images Not Found

```bash
# Use resource path
pandoc doc.md -o doc.pdf \
    --resource-path=.:images:assets

# Or use absolute paths in markdown
![Caption](/absolute/path/to/image.png)
```

#### Citations Not Processing

```bash
# Ensure --citeproc is included
pandoc doc.md -o doc.pdf \
    --citeproc \
    --bibliography=refs.bib

# Check BibTeX file syntax
biber --tool refs.bib
```


## Debug Mode


```bash
# Verbose output
pandoc doc.md -o doc.pdf --verbose

# Show intermediate LaTeX
pandoc doc.md -t latex > debug.tex

# Check Pandoc version and features
pandoc --version

# List supported formats
pandoc --list-input-formats
pandoc --list-output-formats
```
