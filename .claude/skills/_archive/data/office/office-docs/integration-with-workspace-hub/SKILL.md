---
name: office-docs-integration-with-workspace-hub
description: 'Sub-skill of office-docs: Integration with Workspace-Hub.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Integration with Workspace-Hub

## Integration with Workspace-Hub


These skills power document automation across the workspace-hub ecosystem:

```
workspace-hub/
├── documents/
│   ├── templates/           # Uses: docx-templates
│   │   ├── contracts/
│   │   ├── invoices/
│   │   └── reports/
│   ├── generators/          # Uses: python-docx, openpyxl, python-pptx
│   │   ├── report_builder.py
│   │   ├── spreadsheet_gen.py
│   │   └── presentation_gen.py
│   └── processors/          # Uses: pypdf
│       ├── pdf_merger.py
│       └── text_extractor.py
├── output/
│   ├── generated/
│   └── archive/
└── config/
    └── document_config.yaml
```
