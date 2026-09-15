---
name: drive-file-search
description: "Find specific files, examples and prior deliverables through the shared-drive indexes. Use for file/precedent searches; domain datasets and source ownership belong to ecosystem-data-sources."
version: 1.0.0
category: data
related_skills:
- ecosystem-data-sources
triggers:
- similar past work
- do we have files for
- do we have examples of
- do we have precedent for
- search the drives
- prior project
- past project files
- have we done this before
type: reference
freedom: high
---

# Drive File Search — context-aware related-file surfacing

FILE-level asks only; domain-catalog asks belong to `ecosystem-data-sources`.

Resolve tools/configuration against the pinned workspace-hub checkout in task
context, not the skill folder. Missing checkout: unavailable; no unbounded scans.

## Procedure

1. **Extract context** (full detail + worked walkthrough:
   `references/context-extraction.md`). Signals: repo; issue title/labels;
   domain via keywords read live from `.claude/hooks/ecosystem-domain-map.json`
   (generated — never hand-copy its keywords here); artifact-type hints
   (calcs → xlsx/py/csv; CAD → dwg/ipt/step; standards → pdf; simulation → dat/sim/yml/owr).

2. **Build the query** — 2–5 deduped terms (domain keyword + 1–3 title
   words). Pass `--domain <d>` only if `<d>` appears in a `domains:` list in
   `config/drive-index-registry.yml`; else fold the domain word into the terms
   (unknown `--domain` = empty selection, exit 0).

3. **Run the ONE command** (read-only):

   `uv run python scripts/data/drive-index-search/search.py "<terms>" [--domain <d>] --json --limit 20 --caller skill`

   (`python3` if uv is broken.)

4. **Branch on exit code**:
   - `0` — parse the JSON envelope (covers partial and empty results — always
     check `coverage_gaps`).
   - `2` — registry error OR zero reachable indexes: name the down indexes/drives,
     point to `scripts/setup/canonical-drive-links.sh` (PR #3341 if absent), offer
     `ecosystem-data-sources` as fallback.
   - CLI missing — cite issue #3335, fall back to `ecosystem-data-sources`; never
     run ad-hoc drive crawls (bounded reads only).

5. **Present top 10**. Per result: `canonical_path`, `source_index`, `score`,
   `rank_basis` (`meta.*` optional; `raw_path` never shown). Show the canonical
   `/mnt/...` path; why relevant: matched terms, `rank_basis`, extension-vs-hint
   (reorder within equal scores only). Runtime `index_status` and CLI warnings
   govern freshness; registry dates are fallback-only (unknown if absent). Quote each
   `coverage_gaps` `reason` VERBATIM (opaque free text — never
   paraphrase); name the excluded drive. Offer three next actions: open one
   listed file (bounded read); record chosen paths under "Documents consulted" in
   the plan's Resource Intel section; refine terms, re-run once. Zero matches with
   coverage gaps are partial coverage, not proof that no relevant files exist.

## Guardrails (never violate)

- **Read-only**: never write to `/mnt/ace` or `/mnt/dde`; the CLI opens indexes read-only.
- **De-identification** (public repo): drive paths embed client names/project codes.
  Before quoting a surfaced path into an issue, plan, PR, or commit, scan for client
  tokens; if found, describe as metadata only ("a past <domain> deliverable on
  /mnt/ace") or redact. Persisting into public artifacts
  requires the destination's authority. Provider identity grants no extra access.
- **Unreachable drive is normal**: present partial results plus
  the coverage_gaps caveat; never mount, never sudo.
- **Usage playbook** (#3340): integration points, freshness authority, metrics, and
  de-id checklist: `docs/guides/drive-file-search-playbook.md`.

**Related**: `ecosystem-data-sources` (DATA/domain-catalog level).
