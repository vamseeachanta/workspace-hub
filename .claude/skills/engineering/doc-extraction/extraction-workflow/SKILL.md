---
name: doc-extraction-extraction-workflow
description: 'Sub-skill of doc-extraction: Extraction Workflow.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Extraction Workflow

## Extraction Workflow


```
1. Identify document type (standard, report, manual, datasheet)
2. Segment into sections using headings and structure
3. For each section:
   a. Classify content type(s) from Layer 1
   b. Apply Layer 2 engineering patterns
   c. If domain sub-skill applies, delegate to Layer 3
4. Produce structured output (YAML or JSON)
5. Cross-reference extracted items (e.g. equations reference constants)
```
