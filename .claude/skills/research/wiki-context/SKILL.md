---
name: wiki-context
description: "Retrieve bounded curated wiki context and source metadata for domain tasks. Resolve the existing owner checkout and supported query surface; report unavailable operations and missing provenance."
version: 1.0.0
metadata:
  hermes:
    tags: [wiki, context, retrieval, knowledge]
    category: research
    related_skills: [llm-wiki, engineering-issue-workflow]
---

# Wiki Context Retrieval

## Resolve the owner

Use the existing `llm-wiki` checkout supplied in task context or a verified workspace
mapping. Validate the explicit location before reading; missing paths or malformed
configuration are unavailable, not a cue to create a wiki or silently choose another
root. An isolated worktree's sibling directory is not necessarily the owner checkout.

Read owner-relative `llms.txt`, `docs/query-surface.md` and `data/query_sources.json`.
These describe curated knowledge and registered metadata operations. The extraction
corpus handled by workspace-hub's ingestion resolver is a different resource.
Do not change writer fallback behavior or use its returned path as proof of readable
curated content. The legacy `scripts/knowledge/wiki-query-context.sh` assumes
`knowledge/wikis`; do not invoke it for a different layout.

## Bounded retrieval

Run supported commands from the resolved owner checkout, not the skill directory:

```bash
uv run python scripts/llm_wiki_query.py domains list
uv run python scripts/llm_wiki_query.py pages get --path <registered-repo-relative-page>
```

Check current documented commands and registration before invocation. Inspect the
response's `status`, `warnings`, `sources`, `artifact_versions` and `result_count`.
The v1 surface gates `pages search`, `standards get`, `blockers explain` and
`benchmark context` with `not_available`; that status grants no fallback corpus crawl.
`pages get` returns registered page metadata, not proof that source text was read.

For dataset ownership, read the known `data/data-source-catalog.yml` and
`data/domain-database-index.yml` paths directly; they are not assumed registered
query surfaces. Use the selected owner's manifest for numerical-input readiness.
An absent allocation-ledger next hop remains a reported gap.

When task authorization permits reading a specific curated page, choose it through
the domain entrypoint/index identified by `llms.txt` and read only that page. Do not
recursively scan wiki bodies, private archives or licensed originals. Related broad
maintenance and engineering workflows are optional, outside this lookup profile.

## Result and limitations

Return consulted owner-relative paths, source/revision evidence, relevant findings
and access/freshness gaps. Distinguish metadata-only results, read page content and
verified engineering input. Empty results with incomplete access do not establish
absence. A repeated lookup may reuse evidence only while its source version,
permission state and freshness remain applicable.

Consult workspace-hub's `docs/architecture/agent-data-handling-contract.md` when
available. If missing or conflicting with explicit session requirements, state the
gap; do not invent policy or infer redistribution rights from private visibility.
Discovery does not authorize ingestion, publication or changes to source data.
