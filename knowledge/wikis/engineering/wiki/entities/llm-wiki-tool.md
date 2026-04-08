---
title: "LLM Wiki Tool"
tags: [tool, wiki, knowledge-base, ingestion, lint]
sources:
  - llm-wiki-py
added: 2026-04-08
last_updated: 2026-04-08
---

# LLM Wiki Tool

CLI tool for building and maintaining persistent LLM knowledge bases. Based on Karpathy's LLM Wiki pattern.

## Location

`scripts/knowledge/llm_wiki.py`

## Commands

```bash
uv run scripts/knowledge/llm_wiki.py init <domain>
uv run scripts/knowledge/llm_wiki.py ingest <file> --wiki <domain>
uv run scripts/knowledge/llm_wiki.py query "<question>" --wiki <domain>
uv run scripts/knowledge/llm_wiki.py lint --wiki <domain>
uv run scripts/knowledge/llm_wiki.py status --wiki <domain>
uv run scripts/knowledge/llm_wiki.py batch-ingest <metadata_file> --wiki <domain> [--batch-size N] [--dry-run]
```

## Active Wikis

| Wiki | Pages | Domain |
|------|-------|--------|
| marine-engineering | 19,167 | Marine/offshore engineering |
| naval-architecture | 45 | Ship design and stability |
| maritime-law | 22 | Maritime legal cases |
| engineering | new | Repo engineering methodology |

## Schema

Each wiki has:
- `raw/` -- immutable source documents
- `wiki/` -- LLM-maintained markdown pages
- `wiki/index.md` -- content catalog
- `wiki/log.md` -- chronological ingest timeline
- `CLAUDE.md` -- wiki-specific conventions

## Cross-References

- **Related concept**: [[compound-learning-loop]]
- **Related concept**: [[knowledge-to-website-pipeline]]
