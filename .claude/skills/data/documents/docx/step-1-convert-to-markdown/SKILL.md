---
name: docx-step-1-convert-to-markdown
description: 'Sub-skill of docx: Step 1: Convert to Markdown (+4).'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Step 1: Convert to Markdown (+4)

## Step 1: Convert to Markdown


```bash
pandoc document.docx -t markdown -o document.md
```

## Step 2: Plan Changes


Document the specific changes needed before implementation.

## Step 3: Apply Changes in Batches


Apply 3-10 related modifications at a time, preserving formatting.

## Step 4: Validate Changes


Ensure original formatting and unchanged content are preserved.

## Key Principle


When modifying text like "30 days" to "60 days", only mark the changed portion while preserving unchanged runs with their original RSID attributes.
