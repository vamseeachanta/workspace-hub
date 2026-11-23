# knowledge/_archive/

> **Purpose:** durable grave for knowledge-tree content that is superseded or retired.
> **Introduced:** 2026-04-24 via [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482).

## Scope

This tree holds content that was once live under `knowledge/wikis/`, `knowledge/seeds/`, `knowledge/dark-intelligence/`, or sibling knowledge surfaces and has since been superseded, retired, or quarantined by a governance decision.

Files in this tree **are not deleted** because:

- Git history alone is sometimes hard to discover.
- A retired design has institutional value ("why was X rejected?") that should remain findable.
- Quarantine-driven moves (e.g., [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482)) need a landing place that is clearly out-of-retrieval-scope without erasing the history.

## Ingest-scope declaration

`knowledge/_archive/` is **excluded from** all wiki ingest and retrieval surfaces:

- `scripts/data/llm-wiki/ingest-orcina.py` — does not walk `_archive/`
- `scripts/data/llm-wiki/search-wiki.py` — the combined search index does not include `_archive/` (verified via `resolve_wiki_path.py` during the [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482) v3 adversarial review)
- Future MCP `wiki_search` tool ([#2400](https://github.com/vamseeachanta/workspace-hub/issues/2400)) inherits the same exclusion
- Future GTM-boundary linter ([#2485](https://github.com/vamseeachanta/workspace-hub/issues/2485)) excludes `_archive/` from its check surface

If a new ingest path is added, it MUST honor this exclusion. The archive is a grave, not a dormant corpus.

## Naming convention

Archived files retain their full original repo path as a subpath under `knowledge/_archive/`, with a trailing suffix describing the retirement event:

```
knowledge/_archive/<original-parent-path>/<original-basename>-<YYYY-MM-DD>-<reason-slug>.md
```

Example:

```
knowledge/_archive/wikis/engineering/concepts/knowledge-to-website-pipeline-2026-04-08-superseded-by-2482.md
```

The `<YYYY-MM-DD>` is the retirement date (when the move to `_archive/` happened), not the original file creation date. The `<reason-slug>` names the superseding decision (usually an issue number).

## What goes here

- Wiki pages retired by a governance decision (e.g., quarantines per #2482)
- Seed files superseded by promoted wiki pages (rare)
- Research notes whose content was absorbed into durable docs

## What does NOT go here

- Work-in-progress drafts (keep in original location; use branches)
- Temporary intermediate files (delete them; archive is durable)
- Vendor-licensed material with a takedown request (delete; do not archive)
- Client-specific content that shouldn't exist in the repo at all (delete)

## Recovery

If an archived file needs to be brought back:

1. Cite the reason-slug to understand why it was retired
2. Open a PR that restores the file to its original (or a new) live location
3. Update the superseding governance doc / issue to acknowledge the reversal
4. Leave the archived copy in place with a README-style note noting the restoration
