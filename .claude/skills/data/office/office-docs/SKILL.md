---
name: office-docs
version: 1.0.0
category: data
description: Automate Microsoft Office and PDF document workflows including generation,
  manipulation, and template-based document processing.
type: reference
tags: []
scripts_exempt: true
---

# Office Docs

## Overview

This library contains 5 production-ready skills for automating Microsoft Office and PDF document workflows. Each skill covers a specific document type with patterns for generation, manipulation, and template-based automation. Skills follow the Anthropic Skills format with practical examples from real-world document processing pipelines.

## Quick Start

```bash
# Browse available skills
ls skills/office-docs/

# Read a skill
cat skills/office-docs/python-docx/SKILL.md

# Skills are documentation - implement patterns in your document workflows
```

## Native DOCX review parity from HTML reports

When a user asks for a Word review copy to be complete or 1:1 relative to an HTML report, keep the DOCX native/editable where possible and separately inventory every HTML visual channel before claiming parity. Do not rely only on `<img>` tags: count inline SVG, Plotly/JavaScript chart renders, canvas, and embedded data images, then compare against `word/media/*` in the DOCX. See `references/html-report-native-docx-parity.md` for the repair workflow, Playwright capture pattern, and verification snippets.

## Version History

- **1.0.0** (2026-01-17): Initial release with 5 office document skills

---

*These skills represent patterns refined across document automation systems generating thousands of documents daily in production environments.*

## Sub-Skills

- [1. Template Versioning (+3)](1-template-versioning/SKILL.md)

## Sub-Skills

- [Available Skills](available-skills/SKILL.md)
- [Document Creation (+3)](document-creation/SKILL.md)
- [Choose python-docx when: (+4)](choose-python-docx-when/SKILL.md)
- [Python-docx Report Generation (+4)](python-docx-report-generation/SKILL.md)
- [Document Generation Pipeline (+2)](document-generation-pipeline/SKILL.md)
- [Error Handling (+2)](error-handling/SKILL.md)
- [Integration with Workspace-Hub](integration-with-workspace-hub/SKILL.md)
- [Testing Document Generation](testing-document-generation/SKILL.md)
- [Related Resources](related-resources/SKILL.md)
