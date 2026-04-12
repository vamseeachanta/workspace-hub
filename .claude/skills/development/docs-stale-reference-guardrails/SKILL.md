---
name: docs-stale-reference-guardrails
description: Prevent deleted workflow/path references from creeping back into live docs by combining strict scans, legacy allowlists, and shared regex helpers.
version: 1.0.0
tags: [docs, regression-tests, stale-paths, workflow-migration, guardrails]
---

# Docs Stale-Reference Guardrails

Use when a repo has migrated away from old workflow paths (for example `scripts/work-queue/*`, `scripts/agents/*`, `specs/wrk/*`, `.claude/work-queue/*`) and you need to stop live docs from reintroducing those paths.

## When to use
- Historical session logs show repeated reads of deleted paths
- You have already cleaned some docs and want regression protection
- A few legacy/reference docs still need to mention deleted paths intentionally
- You want to shrink the exception surface over time

## Core pattern
Build 3 layers:
1. Strict banned-reference scan for current high-value docs
2. Allowlist-confinement scan for legacy/reference docs only
3. Explicit allowlist-lock test so exceptions cannot quietly grow

## Implementation steps

### 1. Start with a strict curated set
Create a pytest that scans only the cleanest, highest-value live docs first.
Good initial candidates:
- `AGENTS.md`
- `CLAUDE.md`
- `README.md`
- `docs/README.md`
- `docs/plans/README.md`
- workflow templates under `.planning/templates/`
- recently cleaned live docs under `docs/`

Do NOT start by scanning generated reports, archives, or known legacy reference docs.

### 2. Centralize stale-path patterns in a helper
Create a shared test helper, e.g.:
- `tests/helpers/stale_reference_docs.py`

Export:
- `CORE_BANNED_STALE_REFERENCE_PATTERNS`
- `scan_stale_reference_hits(relative_path, patterns=...)`

Core banned families to encode:
- `scripts/work-queue/new-spec.sh`
- `scripts/work-queue/parse-session-logs.sh`
- `scripts/agents/`
- `specs/wrk/WRK-(\d+|NNN)/plan.md`
- deleted work-queue gate scripts:
  - `verify-gate-evidence.py`
  - `generate-html-review.py`
  - `start_stage.py`
  - `exit_stage.py`
  - `verify_checklist.py`
  - `stage_exit_checks.py`
- deleted lifecycle helpers:
  - `close-item.sh`
  - `whats-next.sh`
  - `archive-item.sh`
  - `claim-item.sh`
- `.claude/work-queue/`
- deleted work-queue skill paths

Keep test-specific extra patterns local to the test that needs them.

### 3. Add a strict banned-reference test
Create or maintain a test like:
- `tests/docs/test_banned_stale_references.py`

Pattern:
- curated `STRICT_FILES = [...]`
- loop through each file
- assert `scan_stale_reference_hits(relative_path)` returns no violations

Use this for live/current docs only.

### 4. Add an allowlist-confinement test
Create or maintain a test like:
- `tests/docs/test_legacy_reference_allowlist.py`

Pattern:
- broader `SCAN_FILES = [...]` covering live docs and explicit legacy/reference docs
- tiny `ALLOWED_LEGACY_REFERENCE_FILES = {...}`
- assert stale references appear only in those allowlisted files

This catches stale-path spread while still allowing redirect/reference docs to mention old paths intentionally.

### 5. Lock the allowlist
Add a separate explicit test:
- assert `ALLOWED_LEGACY_REFERENCE_FILES == {...expected files...}`

This is important. Behavioral tests alone do not prevent quiet allowlist growth.

### 6. Expand strict coverage gradually
Workflow:
1. Find next best live docs with the broader scan
2. Clean those docs with minimal wording changes
3. Move them from allowlist/broader scan into strict scan
4. Re-run tests

Good cleanup strategy:
- replace explicit deleted-path mentions with generic wording where possible
- keep the redirect/reference meaning intact
- reserve explicit deleted-path strings only for true legacy mapping docs

## Practical wording pattern for cleanup
Instead of:
- "the old `scripts/agents/*` wrappers are deleted legacy paths"

Prefer:
- "older wrapper-based entrypoints are deleted legacy paths"

Instead of:
- "Do not invoke `scripts/work-queue/close-item.sh`"

Prefer:
- "Do not invoke any legacy local closure helper"

This preserves guidance while satisfying strict stale-path bans.

## Recommended exception docs
In a migrated workflow repo, the allowlist should usually be tiny. Example steady state:
- `docs/ops/legacy-claude-reference-map.md`
- `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md`

If more files are allowlisted, treat that as debt to reduce.

## Verification
Run targeted tests repeatedly while expanding coverage:
- `uv run pytest tests/docs/test_banned_stale_references.py tests/docs/test_legacy_reference_allowlist.py -q`

If there is related audit/export logic, include those tests too.

## Pitfalls
- Do not scan generated reports or archives in the strict test
- Do not rely only on an allowlist behavior test; lock the allowlist explicitly
- Do not duplicate regex lists across tests; centralize them in a helper
- Do not leave live docs in the allowlist just because cleanup is inconvenient; clean and move them into strict coverage when possible

## Outcome to aim for
- Most current docs under strict no-stale-reference enforcement
- Only 1–2 intentional legacy/reference docs allowlisted
- Shared helper owns the core stale-path policy
- Allowlist changes require an explicit reviewed test update
