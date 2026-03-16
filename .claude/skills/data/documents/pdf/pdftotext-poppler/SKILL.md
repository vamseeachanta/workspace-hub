---
name: pdf-pdftotext-poppler
description: 'Sub-skill of pdf: pdftotext (Poppler) (+2).'
version: 1.2.2
category: data
type: reference
scripts_exempt: true
---

# pdftotext (Poppler) (+2)

## pdftotext (Poppler)

```bash
pdftotext document.pdf output.txt
pdftotext -layout document.pdf output.txt  # Preserve layout
```


## qpdf

```bash
# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf document.pdf --pages . 1-5 -- first_five.pdf

# Decrypt
qpdf --decrypt encrypted.pdf decrypted.pdf
```


## pdftk

```bash
# Merge
pdftk file1.pdf file2.pdf cat output merged.pdf

# Split
pdftk document.pdf burst output page_%02d.pdf

# Rotate
pdftk document.pdf cat 1-endeast output rotated.pdf
```
