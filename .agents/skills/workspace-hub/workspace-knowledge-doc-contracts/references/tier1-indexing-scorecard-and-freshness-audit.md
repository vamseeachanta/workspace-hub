# Archived Skill: `tier1-indexing-scorecard-and-freshness-audit`

Original path: `/home/vamsee/.hermes/skills/workspace-hub/tier1-indexing-scorecard-and-freshness-audit`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub/tier1-indexing-scorecard-and-freshness-audit`
Consolidation date: 2026-04-29

---

---
name: tier1-indexing-scorecard-and-freshness-audit
description: Audit tier-1 repos for code-placement/retrieval readiness, write a scorecard report, create follow-up GitHub issues, and add a daily freshness cron while avoiding legacy product-doc reference patterns.
version: 1.0.1
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
- User wants the curation to be maintained on a daily cadence
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
- machine-readable registry (for example `specs/module-registry.yaml` or similar)
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

## Daily freshness automation pattern

If no existing daily repo-curation job covers this need, add a local cron job.
Always list existing cron jobs first so you do not duplicate an already-running maintenance loop.

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

When running an already-scheduled freshness audit (rather than creating the automation):
- Do not add or recommend a new cron job unless explicitly asked; refresh the local latest report only.
- Run the existing audit script if present (for example `scripts/cron/tier1-indexing-freshness.sh`) to get the baseline, but do not blindly trust its terse output.
- Independently verify exact missing surfaces and broken references from the canonical surfaces (`AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/<repo>-operator-map.md`, registry paths).
- Distinguish true broken literal paths/links from intentional glob patterns in code spans. Validate wildcard references with `glob.glob(..., recursive=True)` or shell glob expansion before calling them broken; if they resolve, mention them as glob references only if useful.
- If the stable latest report is overwritten manually with richer findings, also write/copy a dated report for the same day (for example `docs/reports/tier-1-indexing-freshness-YYYY-MM-DD.md`) when that artifact pattern already exists.
- Compare against the prior scorecard assumptions explicitly: note both still-valid assumptions and revisions caused by completed remediations.

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
