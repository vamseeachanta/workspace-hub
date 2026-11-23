# digitalmodel OrcaWave / OrcaFlex Issue Reconciliation

Updated: 2026-04-02
Purpose: reconcile key OrcaWave/OrcaFlex GitHub issues against current repo reality so future engineering and GTM planning start from accurate capability status.

## Executive Summary

The OrcaWave/OrcaFlex domain is already a substantial implementation surface, not a blank-slate initiative. The most important reconciliation finding is that multiple issues still read like greenfield work even though the repo now contains meaningful code, tests, queue tooling, or roadmap artifacts.

For future GTM, this matters because positioning should emphasize:
- existing delivery capability in diffraction, RAO processing, model generation, reporting, and queue orchestration
- near-term proof gaps in integration validation and benchmark-quality evidence
- a smaller set of real credibility blockers rather than a broad "to be built" narrative

## Status categories

- IMPLEMENTED: issue intent largely exists in code/docs already
- PARTIAL: meaningful implementation exists; remaining work is validation, coverage, hardening, or productization
- REAL GAP: still needs substantive engineering work
- DOC/TRACKING: governance or roadmap artifact, not a code gap

## Reconciled issues

| Issue | Title | Reconciled status | Primary machine | Depends on | Evidence | Recommended next action |
|---|---|---|---|---|---|---|
| #1572 | Domain-specific capability roadmaps | DOC/TRACKING | dev-primary | none | `docs/roadmaps/orcawave-orcaflex-capability-roadmap.md` exists; now complemented by `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` | Keep open only if roadmap remains the umbrella tracking issue |
| #1586 | Harden solver queue: batch submission, result watcher, auto post-processing | PARTIAL | dev-primary for code; licensed-win-1 for live operational proof | none | `scripts/solver/submit-batch.sh`, `watch-results.sh`, `post-process-hook.py` exist | Re-scope issue from build to validation/hardening and operational proof |
| #1595 | Solver queue batch submission and result watcher | PARTIAL | dev-primary for reconciliation; licensed-win-1 for live proof | #1586 | Same tooling exists in repo | De-duplicate or close into #1586 after validating real production use |
| #1638 | DiffractionSpec reverse parser | PARTIAL leaning toward IMPLEMENTED | dev-primary | none | `hydrodynamics/diffraction/reverse_parsers.py` exists and `tests/hydrodynamics/diffraction/test_reverse_parsers.py` already contains substantial AQWA + OrcaWave round-trip tests | Verify tests pass in the intended environment, then consider closing or re-scoping to residual edge cases only |
| #1639 | OrcaWave test coverage uplift | PARTIAL | dev-primary | #1638 helpful but not strictly required | `tests/orcawave/`, `tests/hydrodynamics/diffraction/`, `tests/workflows/orcawave/` already exist | Measure current coverage and drive to explicit threshold |
| #1652 | OrcaFlex reporting integration with real `.sim` fixture | REAL GAP | licensed-win-1 for fixture generation, then dev-primary for tests/snapshots | none | Reporting code and tests exist, but real fixture-backed validation still missing | Build minimal committable `.sim` fixture + snapshot test |
| #1656 | OrcaFlex package maturity promotion | PARTIAL | dev-primary | #1652 materially strengthens closure evidence | `src/digitalmodel/orcaflex/` exists with substantial tests already | Convert issue into final maturity review with explicit checklist |
| #1588 | Parametric spec.yml generator | PARTIAL | dev-primary | #1586 improves execution path; hull-library assumptions should be verified first | Strong infrastructure exists in `DiffractionSpec`, diffraction pipeline, hull library | Build the actual bridge artifact and validation harness |
| #1592 | Automate OrcaWave -> OrcaFlex handoff | REAL GAP | split: dev-primary for pipeline code, licensed-win-1 for live `.owr` evidence | #1597 and #1605 | Bridge-related modules exist but no canonical automated handoff | Implement one supported happy-path pipeline |
| #1597 | RAO extractor and DB population pipeline | REAL GAP | split: dev-primary for extractor code, licensed-win-1 for real result capture | #1588 helpful; live `.owr` inputs required for full proof | RAO and DB infrastructure exists, but connection is not clearly productized | Implement extractor + DB writer + evidence fixture |
| #1605 | OrcaWave-to-OrcaFlex integration test | REAL GAP | split: dev-primary test harness + licensed-win-1 artifact generation | #1597 | Export/import related code exists; no canonical integration validation | Add end-to-end validation suite with tolerances |
| #1606 | OrcaWave damping-sweep test suite | INVALID / STALE ISSUE BODY | none until re-scoped | none | Repo search found no `DampingSweep`, `MultiParameterDampingSweep`, `CriticalDampingCalculator`, `BilgeKeelDamping`, or `DampingPeriodAnalyzer` classes; only a simple OrcFxAPI run script exists | Close or rewrite issue from scratch based on actual code present |
| #1264 | OrcaFlex frame analysis | REAL GAP | dev-primary for setup/code, licensed-win-1 for solver validation | none | Broad OrcaFlex tooling exists, but the specific frame-analysis deliverable remains separate | Keep active as a GTM-relevant engineering demo candidate |
| #1292 | OrcaFlex parachute deployment template | REAL GAP | dev-primary for setup/code, licensed-win-1 for dynamic run validation | #1264 recommended first | Specific dynamic template still appears to be future work | Keep active as a differentiated validation/demo scenario |

## Machine assignment summary

### dev-primary only
- #1572
- #1638
- #1639
- most of #1656
- most planning/reconciliation/doc tasks

### dev-primary + licensed-win-1
- #1586 / #1595 for operational proof
- #1652
- #1597
- #1605
- #1592
- #1264
- #1292

### invalid or needs rewrite before assignment
- #1606

## GTM interpretation

### What can already be positioned credibly

1. Diffraction workflow architecture exists
- canonical spec-driven pipeline
- OrcaWave/AQWA conversion infrastructure
- RAO/reporting-oriented utilities

2. OrcaFlex workflow breadth exists
- public package plus deep solver-side implementation
- model building, environment, mooring, riser, pipelay, post-processing, reporting

3. Solver operations story exists
- git-based queue model for licensed execution
- batch submission and result watching present in repo

### What still needs evidence before strong GTM claims

1. Real integration proof
- OrcaWave -> OrcaFlex handoff validation
- real `.sim` and `.owr` artifact-backed tests

2. Benchmark-quality verification
- tolerance-based cross-tool comparisons
- stable regression fixtures

3. Productized extraction story
- RAO extractor to database population
- one-click evidence generation for a reusable demo narrative

## Best next issue order for future GTM support

1. #1652 — real `.sim` fixture and integration evidence
2. #1597 — RAO extractor and database population
3. #1605 — end-to-end OrcaWave to OrcaFlex integration validation
4. #1592 — automate supported handoff workflow
5. #1264 — frame analysis demo-quality template
6. #1292 — dynamic parachute deployment template

## Recommended operating rule

Before starting any OrcaWave/OrcaFlex issue, first classify it:
- Is this actually missing?
- Or is it already implemented and just under-tested / under-documented / under-demonstrated?

This rule is critical for both engineering efficiency and GTM honesty.
