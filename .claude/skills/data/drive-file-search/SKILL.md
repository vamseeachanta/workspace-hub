---
name: drive-file-search
description: "Surface SPECIFIC FILES on the shared drives (/mnt/ace, /mnt/dde) relevant
  to the current task — the FILE-level complement to ecosystem-data-sources (domain-catalog
  level). Extracts query terms from work context, runs the drive-index CLI once,
  presents ranked canonical paths with freshness caveats. Use for similar-past-work,
  prior-project, or files/examples/precedent asks; when domain work needs past deliverables
  (mooring calc → xlsx/py; CAD → dwg/step; standards → PDF inventory)."
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

## Procedure

1. **Extract context** (full detail + worked walkthrough:
   `references/context-extraction.md`). Fail-soft signals: repo name; issue title/labels;
   engineering domain via keywords read live from `.claude/hooks/ecosystem-domain-map.json`
   (generated — never hand-copy its keywords here); artifact-type hints
   (calcs → xlsx/py/csv; CAD → dwg/ipt/step; standards → pdf; simulation → dat/sim/yml/owr).

2. **Build the query** — 2–5 deduped terms (matched domain keyword + 1–3 issue-title
   words). Pass `--domain <d>` only if `<d>` appears in a `domains:` list in
   `config/drive-index-registry.yml`; else fold the domain word into the terms
   (unknown `--domain` = empty selection, exit 0).

3. **Run the ONE command** (read-only):

   `uv run python scripts/data/drive-index-search/search.py "<terms>" [--domain <d>] --json --limit 20`

   (`python3` works when uv is broken.)

4. **Branch on exit code**:
   - `0` — parse the JSON envelope on stdout (covers partial AND empty results — always
     check `coverage_gaps`).
   - `2` — registry error OR zero reachable indexes: name the down indexes/drives,
     point to `scripts/setup/canonical-drive-links.sh` (PR #3341 if absent), offer
     `ecosystem-data-sources` as fallback.
   - CLI missing — cite issue #3335, fall back to `ecosystem-data-sources`; never
     run ad-hoc drive crawls (bounded reads only).

5. **Present top 10**. Required per result: `canonical_path`, `source_index`, `score`,
   `rank_basis` (`meta.*` optional; `raw_path` never shown). Show the canonical
   `/mnt/...` path; why relevant: matched terms, `rank_basis`, extension-vs-hint
   (reorder within equal-score groups only); source index + freshness caveat from the
   registry's `freshness/built_at` ("freshness unknown" if absent). Quote each
   `coverage_gaps` `reason` VERBATIM (opaque free text — never pattern-match or
   paraphrase); name the excluded drive. Offer exactly three next actions: open one
   listed file (bounded read); record chosen paths under "Documents consulted" in the
   plan's Resource Intelligence section; refine terms, re-run once.

## Guardrails (never violate)

- **Read-only**: never write to `/mnt/ace` or `/mnt/dde`; the CLI opens indexes read-only.
- **De-identification** (public repo): drive paths embed client names/project codes.
  Before quoting a surfaced path into an issue, plan, PR, or commit, scan for client
  tokens; if found, describe as metadata only ("a past <domain> deliverable on
  /mnt/ace") or redact. In-session display is fine; persisting into public artifacts
  is the gated act. De-id stays on lane:claude.
- **Unreachable drive is normal** (dde often unmounted): present partial results plus
  the coverage_gaps caveat; never mount, never sudo.

**Related**: `ecosystem-data-sources` (DATA/domain-catalog level).
