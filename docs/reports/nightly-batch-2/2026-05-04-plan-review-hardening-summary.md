# Nightly batch 2/5 plan-review hardening summary — 2026-05-04

Scope: planning/review only. No `status:plan-approved` labels added and no implementation code changed.

## Live queue inventory
- Open `status:plan-review`: #2626, #2541, #2510.
- Open `status:draft`: none by label.
- Open `status:plan-approved`: 28 issues (not modified by this run).

## Selected issues
1. #2626 — live `status:plan-review` but canonical plan file absent from `origin/main`; recovered from dirty control checkout and indexed.
2. #2541 — substantive stale/blocked review evidence; fresh clearance/provenance blockers remained.
3. #2510 — long sustained-MAJOR loop; README and deterministic-GDS contract stale after r14.

## Artifacts created/refreshed
- `docs/plans/nightly-batch-2-prompts/2026-05-04-plan-{2510,2541,2626}-adversarial-rerun.md`
- `scripts/review/results/2026-05-04-plan-2626-{claude,codex,gemini,disagreement}.md`
- `scripts/review/results/2026-05-04-plan-2541-{claude,codex,gemini,disagreement}.md`
- `scripts/review/results/2026-05-04-plan-2510-{claude,codex,gemini,disagreement}.md`

## Current readiness classification
- Approval-ready candidates: none.
- #2626: MAJOR-blocked after Codex/Gemini; plan patched to remove false marker claim, add README row, widen scenario-3 test, define #2552 regression contract, and fix runbook sequencing.
- #2541: MAJOR/data-owner-blocked; plan patched to put clearance before source-body access, require expanded row-level clearance TSV fields, correct `llm_wiki.py` CLI syntax, and demote current 9-column TSV to planning input only.
- #2510: MAJOR-blocked after Codex r15; plan patched for README traceability, deterministic `write_gds(... with_metadata=False, no_empty_cells=True)`, no sidecars, same-process kfactory stderr/cell-registry determinism, and CSV schema/sort key.

## User decisions needed
1. #2541: decide whether SESA project information is citeable and, if yes, provide row-level extraction permissions/allowed content classes (or instruct to park it).
2. #2626: after fresh rerun returns no MAJOR, decide whether to approve the #2552 amendment sequencing before #2552 implementation resumes.
3. #2510: after fresh rerun returns no MAJOR, decide whether to approve the bounded GDSFactory layout/CAD demo despite sustained historical review churn.
