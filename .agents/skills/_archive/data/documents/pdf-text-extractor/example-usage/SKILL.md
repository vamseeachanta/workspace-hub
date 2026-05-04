---
name: pdf-text-extractor-example-usage
description: 'Sub-skill of pdf-text-extractor: Example Usage.'
version: 1.2.0
category: data
type: reference
scripts_exempt: true
---

# Example Usage

## Example Usage


```bash
# Extract single PDF
python extract.py document.pdf --db output.db

# Extract directory
python extract.py /path/to/pdfs --db knowledge.db

# Check progress
python extract.py --stats --db knowledge.db

# With custom chunk size
python extract.py /path/to/pdfs --chunk-size 1500
```
