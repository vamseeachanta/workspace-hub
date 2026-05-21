---
name: tier1-indexing-scorecard-and-freshness-audit
description: Audit tier-1 repos for code-placement/retrieval readiness, write scorecard/freshness reports, create follow-up GitHub issues when requested, and handle daily freshness checks without reinforcing legacy product-doc reference patterns.
version: 1.0.4
category: workspace-hub
---

# Tier-1 Indexing Scorecard and Freshness Audit

Use when the user wants to assess whether tier-1 repos are indexed well enough that:
- new code goes in the right place consistently
- future GitHub issue work can retrieve canonical source/tests/docs paths quickly
- repo curation stays current as repos evolve

## When this skill is the right fit

- User asks for a portfolio review of tier-1 repos focused on code placement, retrieval, indexing, or repo curation
- User wants a report file plus a concrete GitHub issue set
- User wants the curation to be checked or maintained on a daily cadence
- User explicitly wants to avoid legacy product-doc references in reporting/planning artifacts

## Core rule learned from live use

Do not frame trusted routing surfaces using legacy product-doc references, even if old docs still mention them.
In reports/issues, prefer current canonical routing surfaces such as:
- repo workflow contract
- top-level README
- repo docs entry point
- repo operator map under `docs/maps/`
- canonical machine-readable registries

If old docs still reference legacy product-doc files, describe them as:
- legacy product-doc references
- stale legacy references
- missing product-doc references

## Audit workflow

### Freshness-only scheduled/audit mode

When the user asks for a scheduled or daily freshness audit, do **not** assume the task includes creating or editing cron jobs. Treat scheduling as out of scope unless the user explicitly asks for cron setup. The default deliverable is a local refresh of `docs/reports/tier-1-indexing-freshness-latest.md` with a current timestamp, current evidence, and a clear statement that no new cron jobs were scheduled.

For the current tier-1 repo set (`workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`), inspect these canonical routing/index surfaces first:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- repo-local operator map under `docs/maps/<repo>-operator-map.md` when applicable
- `docs/registry/module-routing.yaml` when applicable

When the requested working directory is `/mnt/local-analysis/workspace-hub`, prefer nested repo paths under that tree (`/mnt/local-analysis/workspace-hub/<repo>`). Sibling paths under `/mnt/local-analysis/<repo>` may exist; use them only as fallback if the nested repo is absent so the refreshed local report reflects the requested workspace checkout.

For freshness reports, include:
- date/time
- per-repo status (`green` / `yellow` / `red`)
- exact broken or missing surfaces
- concise next actions
- whether the 2026-04-22 tier-1 indexing scorecard assumptions still hold or need revision

Use “no material drift detected at the status level” when repo statuses are unchanged but the scan surfaces additional non-status-changing evidence. Do not overstate as “no material drift” if newly detected broken references were added to the report.

When including verification evidence, avoid embedding exact `stat` size/mtime/checksum values inside the report until all report edits are complete. A safer pattern is: write the full report, finish all patches, run final `stat`/`sha256sum`, then put exact verification values in the final cron response (or append them only as the last report edit).

Before final delivery, deduplicate generated broken-reference evidence by `(repo, source file, line, target)`. The scanner/generator may surface the same Markdown link through multiple paths; keep one confirmed finding in the summary table and detailed section rather than inflating broken-link counts.

If the existing `tier-1-indexing-freshness-latest.md` contains stale status or stale broken-link counts from a prior generator, explicitly note the correction in the refreshed report. Do not silently preserve stale counts: re-run false-positive-filtered checks, keep `aceengineer-website` red until `docs/registry/module-routing.yaml` exists, and keep `assetutilities` yellow when the only confirmed remaining issue is trusted-path runtime/cache/log/report noise.

### 1. Load context and identify tier-1 repos
Read:
- `docs/BUSINESS_BRAIN.md`
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
- `docs/README.md`
- `docs/standards/FILE_STRUCTURE_TAXONOMY.md`
- `docs/standards/DATA_PLACEMENT.md`

Use `session_search` with broad recall terms if prior portfolio/indexing work likely exists.

### 2. Inventory each tier-1 repo
For each repo, inspect whether these surfaces exist and are trustworthy:
- workflow contract file
- top-level README
- repo docs entry point
- repo operator maps
- domain docs when relevant
- machine-readable registry (prefer `docs/registry/module-routing.yaml` for current tier-1 routing; only use older `specs/module-registry.yaml`-style files when the repo already documents them as canonical)
- source tree
- tests tree
- CI workflow directory

Also inspect:
- root clutter/noise
- backup artifacts in source paths (`*.bak`, `*.orig`)
- weak source/test parity
- broken references in README/docs

### 3. Score the repos
Use a compact 4-axis rubric:
- Mission clarity
- Code placement guidance
- Retrieval readiness
- Index hygiene

Keep scoring directional, not pseudo-precise. The report should explain why each repo scored as it did.

### 4. Write a scorecard report
Write a report under `docs/reports/YYYY-MM-DD-tier-1-indexing-scorecard.md`.

Recommended sections:
1. Executive summary
2. Scoring rubric
3. Scorecard table
4. Per-repo findings
5. Portfolio-level gaps
6. Recommended target contract for every tier-1 repo
7. Priority order
8. Proposed follow-on issue set
9. Daily maintenance requirement

## GitHub issue creation pattern

After writing the report, create:
1. One contract issue for the tier-1 indexing/code-placement standard
2. One repo-specific remediation issue per tier-1 repo
3. One automation issue for daily freshness auditing

If the user asks to continue beyond the scorecard/issue seeding step, the next default move is to enter the standard GitHub planning workflow for the contract issue first:
- draft `docs/plans/YYYY-MM-DD-issue-<contract>-...md`
- update `docs/plans/README.md`
- keep status `draft` until adversarial review artifacts exist

Suggested pattern from live use:
- contract issue
- assetutilities remediation
- digitalmodel remediation
- aceengineer-website remediation
- workspace-hub curation cleanup
- daily freshness audit automation

### Important issue-body guidance
- Use `--body-file` temp markdown files
- Create the contract issue first
- Patch child issue bodies to replace placeholders like `<CONTRACT_ISSUE>` with the real issue number
- Verify every created issue immediately with `gh issue view --json ...`
- Post one linking comment on the contract issue listing all child issues


## Freshness scan false-positive guardrails

When extracting broken references from canonical docs, avoid these common false positives:
- wildcard routing patterns such as `*.html`, `content/*.html`, or `tests/unit/test_common_*.py` are patterns, not literal missing files
- descriptive module names in overview tables (for example `engine.py`, `calculation.py`, `math_helpers.py`) are not broken paths unless the surrounding text presents them as canonical file links
- naming-convention placeholders such as `feature-name.md` are examples, not missing files
- relative links should be resolved from the file that contains the link; if the visible label is bare but the Markdown target includes a directory (for example `modules/ai/AI_AGENT_GUIDELINES.md`), check the target, not only the label

Known current evidence pattern from 2026-05-08: `digitalmodel/docs/maps/digitalmodel-operator-map.md` referenced `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` as if repo-local while the matching file existed at the workspace-level map path; report this as a stale repo-local routing reference unless fixed.

Latest evidence references:
- `references/2026-05-08-freshness-audit-lessons.md` — compact evidence snapshot, false-positive filters, and validation checklist from the 2026-05-08 scheduled freshness audit.
- `references/2026-05-09-freshness-audit-lessons.md` — status-level baseline and scanner false-positive refinements from the 2026-05-09 scheduled audit.
- `references/2026-05-10-freshness-audit-lessons.md` — updated evidence: `assetutilities` broken-link findings refined as false positives, `aceengineer-website` remains RED for missing registry, and report verification evidence should be included when available.
- `references/2026-05-11-freshness-audit-lessons.md` — status-level baseline, nested-repo path guardrail, current stale-reference evidence, and report verification evidence from the 2026-05-11 scheduled audit.
- `references/2026-05-12-freshness-audit-lessons.md` — status-level baseline, unchanged-status wording, current stale-reference evidence, and the report verification pitfall about not embedding exact checksums before final report edits.
- `references/2026-05-14-freshness-audit-lessons.md` — status-level baseline, corrected stale previous-report content (`assetutilities` broken-link false positive and `aceengineer-website` RED registry status), and current evidence snapshot.
- `references/2026-05-15-freshness-audit-lessons.md` — latest status-level baseline, report readback/verification pattern, historical-scorecard-as-context guardrail, and current evidence snapshot.
- `references/2026-05-20-freshness-audit-lessons.md` — dedupe generated broken-reference evidence before finalizing, verify file status/mtime/hash after all report patches, and preserve the corrected RED/YELLOW tier-1 status baseline.
- `references/2026-05-21-freshness-audit-lessons.md` — compaction-resume closeout pattern, byte-identical dated/latest verification, status-level drift wording, and sibling-checkout generator path drift handling.


## Daily freshness automation pattern

If no existing daily repo-curation job covers this need and the user explicitly asks to create or repair automation, add a local cron job.
Always list existing cron jobs first so you do not duplicate an already-running maintenance loop. If the user says not to schedule new cron jobs, only refresh the report and state that no new cron jobs were scheduled.

Recommended job shape:
- schedule: daily early morning local time
- deliver: `local`
- prompt goal: audit tier-1 routing/index freshness
- refresh a stable latest report path, e.g.
  `docs/reports/tier-1-indexing-freshness-latest.md`

The daily audit should check:
- canonical entry points still exist
- operator maps exist where required
- registry references are not stale/broken
- trusted source paths are free of backup/cache/runtime noise
- scorecard assumptions still hold or need revision

## Good output artifacts

### Report 1
- `docs/reports/YYYY-MM-DD-tier-1-indexing-scorecard.md`

### Report 2
- `docs/reports/tier-1-indexing-freshness-latest.md`

### Issue set
- contract issue
- repo-specific child issues
- automation issue

## Pitfalls

1. Do not rely on raw inventory files as curated routing surfaces.
   Example: a massive `docs/CONTENT_INDEX.md` may be useful inventory but too noisy for issue routing.

2. Do not repeat or reinforce legacy product-doc references in new planning/reporting artifacts.

3. Do not create child issues with unresolved placeholders. Replace placeholders with the real parent issue number before creation.

4. Do not assume a newly created cron job has already written the report. If needed, write an initial freshness report immediately so the file exists from day one.

5. Distinguish between:
- strongest repo structurally
- strongest control-plane repo
These may be different repos.

## Reusable conclusion pattern

A common outcome is:
- `digitalmodel` = strongest source/test engineering structure but incomplete repo-wide routing surfaces
- `workspace-hub` = richest control plane but noisy curation/index hygiene
- `assetutilities` = highest risk of code misplacement
- `aceengineer-website` = understandable for direct edits but weak durable issue-routing
