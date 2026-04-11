# Wiki: engineering
> Engineering methodology — how the workspace-hub ecosystem is built and operated.
> Complements domain wikis (marine-engineering, maritime-law, naval-architecture).
## Quick Ref
- Schema & runbook: [SCHEMA.md](SCHEMA.md) | Sources: [SOURCE_INVENTORY.md](SOURCE_INVENTORY.md)
- Index: [wiki/index.md](wiki/index.md) | Log: [wiki/log.md](wiki/log.md)
- Pages: `wiki/{concepts,entities,sources,standards,workflows}/`
- Frontmatter: `title`, `tags`, `sources`, `added`, `last_updated`
## Ingest
1. Read source → 2. Extract → 3. Create pages → 4. Update index → 5. Append log
## Lint
Orphans, broken refs, missing index entries, stale pages, missing concept pages
## Architecture Context
Parent operating model: [LLM-Wiki + Resource/Document Intelligence Operating Model](../../docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md) (#2205)
