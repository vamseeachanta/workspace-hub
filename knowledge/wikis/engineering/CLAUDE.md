# Wiki: engineering
> Engineering methodology — how the workspace-hub ecosystem is built and operated.
> Complements domain wikis (marine-engineering, maritime-law, naval-architecture).
## Quick Ref
- Schema & runbook: [SCHEMA.md](SCHEMA.md) | Sources: [SOURCE_INVENTORY.md](SOURCE_INVENTORY.md)
- Index: [wiki/index.md](wiki/index.md) | Log: [wiki/log.md](wiki/log.md)
- Pages: `wiki/{concepts,entities,sources,standards,workflows}/`
- Frontmatter: see **Frontmatter Schema** below

## Frontmatter Schema

All wiki pages use YAML frontmatter (`---` delimited) with the following fields:

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `title` | **required** | string | Page title |
| `tags` | **required** | list | Classification tags, e.g. `[cfd, openfoam]` |
| `added` | **required** | date | ISO date when page was created (`YYYY-MM-DD`) |
| `last_updated` | **required** | date | ISO date of last modification (`YYYY-MM-DD`) |
| `sources` | recommended | list | Source documents referenced, e.g. `[dnv-rp-b401]` |
| `domain` | optional | string | Explicit domain classification |
| `cross_links` | optional | list | Cross-wiki references (e.g. `[marine-engineering/entities/anode]`) |

Example:
```yaml
---
title: "My Page Title"
tags: [concept-a, concept-b]
sources:
  - source-document-name
added: 2026-04-08
last_updated: 2026-04-08
---
```

## Ingest
1. Read source → 2. Extract → 3. Create pages → 4. Update index → 5. Append log
## Lint
Orphans, broken refs, missing index entries, stale pages, missing concept pages
## Architecture Context
Parent operating model: [LLM-Wiki + Resource/Document Intelligence Operating Model](../../docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md) (#2205)
