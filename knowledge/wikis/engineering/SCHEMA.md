# Engineering Wiki — Schema & Operator Runbook

> Full schema, conventions, and operator runbook for the engineering wiki.
> Referenced from CLAUDE.md. See also: SOURCE_INVENTORY.md for ingest source classes.

## Directory Structure

```
raw/          # Immutable source documents (LLM reads, never modifies)
  methodology/# Methodology docs (compound engineering, enforcement, etc.)
  modules/    # Module documentation snapshots
  learnings/  # Session learnings and memory topics
  assets/     # Images and figures extracted from sources
wiki/         # LLM-maintained markdown pages
  index.md    # Content catalog — every page listed with link + 1-line summary
  log.md      # Chronological timeline of ingests, queries, lint passes
  overview.md # High-level domain synthesis
  entities/   # Entity pages (specific tools, repos, systems: OrcaFlex, solver-queue, etc.)
  concepts/   # Concept pages (patterns: TDD, enforcement-over-instruction, compound-loop)
  sources/    # Source summary pages (one per ingested document)
  standards/  # Standards reference pages (API, DNV, ASME, etc.)
  workflows/  # Engineering methodology workflows and pipelines
  comparisons/# Filed query outputs (tables, analyses, comparisons)
  visualizations/ # matplotlib plots, Marp slide decks
```

## Conventions

### Page format
- Title in YAML frontmatter
- Tags for categorization
- Cross-references as markdown links: `[[entity-name]]` or `[text](../concepts/topic.md)`

### Index format (index.md)
```yaml
---
last_updated: YYYY-MM-DD
page_count: N
source_count: N
---

## Entities

| Page | Summary | Last Updated |
|------|---------|-------------|
| [[Page Name]](path) | 1-line summary | YYYY-MM-DD |

## Concepts

...

## Sources

...
```

### Log format (log.md)
Each entry starts with a consistent prefix for easy grep:
```
## [YYYY-MM-DD] ingest | Source Title
- Processed: source_file.pdf
- Pages updated: index.md, entities/entity1.md, concepts/concept1.md
- Notes: <brief notes>

## [YYYY-MM-DD] query | Question text
- Pages consulted: entities/...
- Answer filed: comparisons/...
```

## Ingest Workflow

1. Read source document
2. Extract key entities, concepts, facts
3. Create/update source summary in wiki/sources/
4. Update/create entity pages in wiki/entities/
5. Update/create concept pages in wiki/concepts/
6. Update wiki/index.md with new entries
7. Append entry to wiki/log.md

## Lint Workflow

Check for:
1. Contradictions between pages
2. Stale claims superseded by newer sources
3. Orphan pages (no inbound links)
4. Missing cross-references
5. Concepts mentioned but lacking their own page
6. Data gaps fillable by external sources

## Operator Runbook

### Seed (one-time, already done)
```bash
uv run scripts/knowledge/llm_wiki.py init engineering
# Then manually create pages from source classes (see SOURCE_INVENTORY.md)
```

### Incremental Ingest (repeatable)
```bash
# 1. Check current status
uv run scripts/knowledge/llm_wiki.py status --wiki engineering

# 2. Ingest a new source file
uv run scripts/knowledge/llm_wiki.py ingest <path/to/file> --wiki engineering

# 3. Batch ingest from metadata file
uv run scripts/knowledge/llm_wiki.py batch-ingest <metadata.yaml> --wiki engineering --dry-run
uv run scripts/knowledge/llm_wiki.py batch-ingest <metadata.yaml> --wiki engineering

# 4. After ingest: verify index updated, log appended
uv run scripts/knowledge/llm_wiki.py status --wiki engineering
```

### Lint (quality check)
```bash
uv run scripts/knowledge/llm_wiki.py lint --wiki engineering
```

Lint checks:
1. Orphan pages (no inbound links from index or other pages)
2. Broken cross-references (`[[missing-page]]`)
3. Pages missing from index.md
4. Stale pages (last_updated > 90 days)
5. Concepts mentioned in text but lacking their own page

### Manual Ingest Procedure (when CLI ingest insufficient)
For source classes that need Claude Code interpretation (methodology docs, session learnings):
1. Read the source file
2. Classify content as entity or concept
3. Create wiki page in `wiki/entities/` or `wiki/concepts/` using frontmatter template
4. Create source summary page in `wiki/sources/`
5. Add cross-references to related pages
6. Update `wiki/index.md` with new entry row
7. Append entry to `wiki/log.md`

### Future: Cronized Ingest
Target: nightly cron that scans for new/modified sources and triggers ingest.
Candidate script: `scripts/knowledge/wiki-ingest-cron.sh` (not yet created).
