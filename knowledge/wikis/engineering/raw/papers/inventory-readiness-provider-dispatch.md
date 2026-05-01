# Archived Skill: `inventory-readiness-provider-dispatch`

Original path: `/home/vamsee/.hermes/skills/ai/inventory-readiness-provider-dispatch`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/ai/inventory-readiness-provider-dispatch`
Consolidation date: 2026-04-29

---

---
name: inventory-readiness-provider-dispatch
description: Build and operate a computable readiness matrix that connects raw-data-to-GTM package stages with Claude/Codex/Gemini dispatch lanes and weekly credit pacing.
version: 1.0.0
category: ai
type: workflow
tags:
  - provider-routing
  - inventory-readiness
  - github-issues
  - quota-management
  - llm-wiki
  - gtm
related_skills:
  - agent-usage-optimizer
  - gh-work-execution
  - multi-provider-adversarial-review
---

# Inventory Readiness Provider Dispatch

Use this when the user wants to optimize Claude/Codex/Gemini usage around a staged GitHub work pipeline, especially:

`raw data -> inventory -> llm-wiki -> calculation code -> parametric outputs -> website/GTM`

The key lesson: do not rely only on narrative backlog notes or a provider work queue. Create a machine-readable readiness matrix that makes package stage status, evidence, downstream issue refs, and provider dispatch lanes computable.

## Canonical Workspace-Hub Pattern

For workspace-hub, the implemented pattern from #2487 is:

- canonical matrix: `config/knowledge/inventory-readiness.yaml`
- validator/renderer: `scripts/knowledge/validate_inventory_readiness.py`
- derived report: `docs/reports/inventory-readiness-matrix-YYYY-MM-DD.md`
- targeted tests: `tests/knowledge/test_inventory_readiness.py`

The Markdown report should be generated from YAML, not hand-authored as the source of truth.

## Required Workflow Gate

All packages surfaced by the matrix must follow:

`plan -> adversarial plan review -> user approval -> implementation -> adversarial implementation review -> closeout`

Do not execute downstream issue candidates just because they appear in the matrix. Keep them as references/candidates/dependencies unless explicitly approved for execution.

## Provider Fit

- Gemini: raw data discovery, source inventory, standards/competitor/GTM scouting, gap discovery.
- Claude: plan synthesis, adversarial plan review, governance/architecture decisions, implementation review.
- Codex: calculation code, validators, tests, CI fixes, bounded implementation/refactors, deterministic report generation.

Avoid burning Claude on mechanical coding when Codex has credits and the task is bounded.

## Weekly Credit Pacing Policy

Goal: keep long-running provider-ready packages staged ahead of time so work can execute continuously while credits are available.

- Target about 90% weekly usage by day 5.
- Preserve about 10% for the final 2 days.
- Apply this only when quota telemetry is sufficient.
- If telemetry is weak, route directionally using the provider scorecard plus the readiness matrix, and state confidence limits.

## Matrix Contents

Each package family should include:

1. package/stage names for the full pipeline
2. readiness status per stage, e.g. `READY`, `PARTIAL`, `BLOCKED`, `MISSING`, `STALE`
3. evidence for every non-ready stage
4. downstream issue references with role/approval state
5. provider dispatch lanes for Codex/Gemini/Claude
6. dependency issues needed to make the lane executable
7. explicit boundary text for downstream/reference-only work

## Validation Rules Learned from #2487

Add regression tests and validator rules for these pitfalls:

1. Blocked/partial/missing/stale evidence must be explicit in the rendered report. A plain status label is not enough for dispatch.
2. Dispatch `dependency_issues` must mirror all actionable/non-reference issue refs in stage evidence. Otherwise valid downstream work silently disappears from provider queues.
3. Reference-only issues should be allowed in evidence but excluded from actionable dependency-mirror requirements.
4. Provider queue counts should be labeled as observed values, not acceptance thresholds, because utilization snapshots age quickly.
5. Downstream issues must remain references/candidates/dependencies unless the current approved scope explicitly includes execution.

## TDD Implementation Checklist

1. Verify issue gate and approval state before coding.
2. Write failing tests first for schema, allowed statuses, required stages, provider lanes, downstream refs, CLI behavior, report content, and evidence requirements.
3. Implement the minimal validator/config/report needed to pass tests.
4. Add negative tests for missing evidence and missing dispatch dependency mirrors.
5. Render the report deterministically.
6. Run targeted tests and validator commands.
7. Run adversarial implementation review before closeout.
8. Commit generated source/config/report/review artifacts together.
9. Post closeout evidence and close only after validation + review pass.

## Useful Commands

```bash
uv run pytest tests/knowledge/test_inventory_readiness.py -q
uv run python scripts/knowledge/validate_inventory_readiness.py \
  --config config/knowledge/inventory-readiness.yaml \
  --validate-only
uv run python scripts/knowledge/validate_inventory_readiness.py \
  --config config/knowledge/inventory-readiness.yaml \
  --output docs/reports/inventory-readiness-matrix-$(date +%F).md
uv run python -m py_compile scripts/knowledge/validate_inventory_readiness.py
```

## Closeout Evidence

Before closing, capture:

- test result count
- validator pass output
- report render output
- py_compile pass
- adversarial implementation review verdicts
- commit hash
- GitHub closeout comment URL
