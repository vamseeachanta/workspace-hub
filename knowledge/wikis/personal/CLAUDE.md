# Wiki: personal

> Personal knowledge wiki — career, professional development, and individual reference material.

## Frontmatter Schema

All wiki pages use YAML frontmatter (`---` delimited) with the following fields:

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `title` | **required** | string | Page title |
| `tags` | **required** | list | Classification tags, e.g. `[software, python]` |
| `added` | **required** | date | ISO date when page was created (`YYYY-MM-DD`) |
| `last_updated` | **required** | date | ISO date of last modification (`YYYY-MM-DD`) |
| `sources` | recommended | list | Source documents referenced |
| `domain` | optional | string | Explicit domain classification |
| `cross_links` | optional | list | Cross-wiki references (e.g. `[engineering/concepts/compound-engineering]`) |

Example:
```yaml
---
title: "Python Type Safety"
tags: [software, python, mypy]
sources:
  - career-learnings
added: 2026-04-09
last_updated: 2026-04-09
---
```

## Quick Ref

- Index: [wiki/index.md](wiki/index.md)
- Pages: `wiki/`

## Architecture Context

Parent operating model: [LLM-Wiki + Resource/Document Intelligence Operating Model](../../docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md) (#2205)
