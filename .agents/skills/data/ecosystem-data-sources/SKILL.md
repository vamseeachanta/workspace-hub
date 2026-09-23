---
name: ecosystem-data-sources
description: "Find existing engineering datasets, source ownership and readiness before analysis or database work. Use for 'do we have data for X', source selection and reference-data discovery; specific file searches belong to drive-file-search."
version: 1.0.0
category: data
related_skills:
- research-literature
- worldenergydata-source-readiness
triggers:
- do we have data for
- where do we get data
- what data do we have
- build the database
- establish the database
- data sources for
- riser data
- mooring data
- metocean data
- reference data for
type: reference
freedom: high
---

# Ecosystem Data Sources — proactive surfacing

## Bounded lookup

Resolve the existing `llm-wiki` checkout from explicit task context or a verified
workspace mapping. Do not assume it is nested under the current checkout or next
to an isolated worktree. A missing explicit location is unavailable; do not create
a replacement wiki or crawl the workspace.

Read `llms.txt`, then these known paths relative to that owner root:
- `data/data-source-catalog.yml`: source IDs, rights, routes and domain associations.
- `data/domain-database-index.yml`: domain tables, seed-source IDs, consuming
  calculations and linked issues. Read current entries rather than copied counts.

The wiki query CLI does not necessarily register these catalogs. Read the known
files directly; do not invent a query operation. Follow the selected dataset's
owner manifest before treating values as computational input. Missing manifests
or allocation-ledger references are gaps, not permission to create a new registry.

Return the domain, matching source IDs, owner, source/manifest revision, freshness
basis, intended-use readiness and linked issue where recorded. Distinguish a
catalog entry from acquired, verified data. Name unavailable sources and unknown
rights or readiness. Use `drive-file-search` for a bounded specific-file lookup.

## Source rights and authority

This skill authorizes discovery only. Source rights, source ownership and publication
permission are separate. Do not infer copying rights from private repository visibility.

Consult `docs/architecture/agent-data-handling-contract.md` in workspace-hub when
present. If absent or contradictory, report the gap and retain explicit session
requirements; do not invent replacement policy. The supplied raw-evidence rule
requires client-supplied/measured originals in the owning private repository under
`data/<dataset>/raw/`, with SHA-256 digests and an extraction manifest. This lookup
does not perform that ingest. Vendor-licensed standards originals remain outside
Git at their licensed location; only permitted derivatives may be retained.

Treat `ACE_SHARE_ROOT` precedent as restricted discovery metadata until its rights
and owner are established. Keep client names, raw paths and restricted content out
of public artifacts; perform only bounded reads. A source-rights conflict remains
unresolved for copying/publication even when metadata lookup can continue.

Choose execution by verified access and capability; provider names do not assign
authority. Related skills are optional references, not an instruction to activate
another workflow or expand the approved task profile.
