---
id: digitalmodel#458
title: "GZ curve digitization from PNA and Biran figures"
type: standard
status: working
priority: medium
complexity: moderate
route: B
created_at: 2026-03-19
target_repos: [workspace-hub, digitalmodel]
computer: dev-primary
plan_workstations: [dev-primary]
execution_workstations: [dev-primary]
category: document-intelligence
subcategory: curve-digitization
blocked_by: []
github_issue_ref: https://github.com/vamseeachanta/digitalmodel/issues/458
plan_reviewed: true
plan_approved: true
spec_ref: .claude/work-queue/assets/WRK-1381/plan.md
claim_routing_ref: .claude/work-queue/assets/WRK-1381/claim-evidence.yaml
stage_evidence_ref: .claude/work-queue/assets/WRK-1381/evidence/stage-evidence.yaml
claim_quota_snapshot_ref: config/ai-tools/agent-quota-latest.json
---
## Mission

7,390 figure references exist in curves/index.jsonl but zero are digitized. GZ curves (righting arm vs heel angle) are the most valuable for TDD — they provide complete validation datasets for stability calculations.

## What

1. Filter curves/index.jsonl for GZ-curve figures (caption contains "GZ", "righting arm", "stability curve")
2. Extract/digitize GZ curves from PNA Vol I, Biran, EN400 cross curves
3. Store as YAML arrays: heel_angles_deg + GZ_values_m
4. Create `data/doc-intelligence/digitized-curves/gz-curves.yaml`
5. Wire into stability module test fixtures

## Reference Sources

- PNA-GZ-Curves.manifest.yaml (dedicated GZ curve document)
- Biran Ship Hydrostatics — Ch 6-7: stability curves
- EN400 Ship Data Section — cross curves for 6 vessels

## Acceptance Criteria

1. ≥ 10 GZ curves digitized with source traceability
2. Curves stored in standard YAML format
3. Test fixtures created for stability module validation
4. Digitization accuracy ≤ 2% of source values

## Plan

> **Route B planning note**: authoritative plan is inline in this WRK per repo policy.

**Objective**: close the gap between the WRK mission ("digitize source figures") and the
current repo state ("3 existing traced fixture conditions") by splitting execution into
two explicit deliverables:
- `A)` source-digitization corpus work, which requires source-figure availability and a
  measurable accuracy method
- `B)` downstream `digitalmodel` fixture/test integration, which is where the TDD work
  starts

**Planning stance**: execution may begin with `B` only if `A` is formally blocked and
recorded as a dependency; otherwise the WRK scope must stay tied to true figure
digitization rather than simple fixture expansion.

| Phase | Target | Key deliverable |
|---|---|---|
| **0** | Source dependency resolution | Explicit inventory of which target curves come from accessible figures vs already-tabulated values |
| **1** | Fixture schema + TDD guardrails | Canonical condition schema and failing tests for count, traceability, units, and provenance |
| **2** | Source-digitization method | Declared extraction path for figure-backed curves plus defined accuracy check |
| **3** | Dedicated GZ fixture expansion in `digitalmodel` | `gz_curves.yaml` expanded to `>= 10` traced conditions with per-condition provenance |
| **4** | Shared artifact bridge | Mandatory implementation or explicit blocker resolution for `data/doc-intelligence/digitized-curves/gz-curves.yaml` |
| **5** | Verification + alignment | Repo tests, fixture integrity checks, issue evidence, and WRK gate artifacts updated |

**Scripts-over-LLM audit**:
- No existing script in the current workspace snapshot already performs GZ curve extraction
  or fixture expansion for this WRK.
- Existing reusable automation is limited to gate orchestration and verification, not
  the domain fixture build itself.
- Result: implementation should reuse existing test/fixture patterns, not invent a new
  workflow script prematurely.

**Pseudocode**:
1. Read current `gz_curves.yaml` and enumerate condition count, field set, unit system,
   and source-traceability coverage.
2. Write failing tests that assert:
   - minimum condition count,
   - required traceability keys on every condition,
   - stable schema expectations for imperial/metric fields.
3. Resolve source-of-truth per target curve:
   - figure-backed digitization from accessible PNA/Biran/EN400 assets, or
   - exact transcription from already-tabulated in-repo values.
4. For figure-backed curves, declare the digitization tool/method and calibration basis;
   for tabulated curves, mark them as transcription-backed rather than image-digitized.
5. Expand fixture conditions only after provenance class is explicit for every added
   condition, then verify no condition violates the expected GZ/KN relationship or
   documented tolerance.
6. Write the shared artifact at `data/doc-intelligence/digitized-curves/gz-curves.yaml`
   in this WRK, or stop and revise acceptance criteria before execution proceeds.

**Test plan**:
1. Add a failing test that asserts `len(conditions) >= 10`.
2. Add a failing test that every condition includes explicit source-traceability fields
   such as source label/reference/page-or-figure metadata.
3. Add a failing test that each condition has one coherent unit system and the expected
   value arrays for that system.
4. Add a failing test that every condition declares `provenance_type` as either
   `figure_digitized` or `tabulated_transcription`.
5. Add a failing test that figure-digitized conditions include enough checkpoint data to
   compute the accuracy metric against source values.
6. Keep existing numerical validation tests for `gz_from_cross_curves()` passing for all
   conditions that use KN-derived data.
7. Validate that the expanded fixture remains YAML-loadable and structurally stable.
8. Run the focused naval-architecture pytest target for GZ/stability coverage.

**Accuracy method (AC #4)**:
- For `tabulated_transcription` conditions: acceptance is exact value transcription
  against published tabulated checkpoints; the 2% criterion is trivially satisfied and
  recorded as `0% transcription delta`.
- For `figure_digitized` conditions: compare digitized curve values against at least 5
  source checkpoints per curve and compute absolute percent error relative to the source
  checkpoint value, with pass criterion `max_error_pct <= 2.0`.
- If no authoritative checkpoints can be established for a figure, that condition does
  not satisfy AC #4 and may not count toward the `>= 10` target.

**Key constraints**:
- Current source-side assets referenced by the WRK are not present in the active workspace
  snapshot. That is a real dependency, not just a note.
- If PNA/Biran/EN400 figure assets remain unavailable, the WRK must either:
  - be formally narrowed to transcription/integration work, or
  - stop before claim/activation as source-blocked.
- Claim/activation must wait until Stage 5 and Stage 7 review evidence exists.

**Expected output shape**:
- Updated `digitalmodel/tests/fixtures/test_vectors/naval_architecture/gz_curves.yaml`
- Updated `digitalmodel/tests/naval_architecture/test_gz_curves.py`
- Implemented shared artifact `data/doc-intelligence/digitized-curves/gz-curves.yaml`
- Per-condition provenance metadata sufficient to distinguish digitized vs transcribed data

## Session Handoff

### Work Done This Session
- Expanded `digitalmodel` GZ validation fixtures from 3 to 10 traced conditions.
- Added contract tests for minimum condition count, required `provenance_type`, and
  required checkpoint / error metadata for any future `figure_digitized` condition.
- Added shared corpus artifact:
  `digitalmodel/data/doc-intelligence/digitized-curves/gz-curves.yaml`
- Added shared-artifact contract coverage in
  `digitalmodel/tests/naval_architecture/test_gz_curves.py`.
- Registered the shared corpus in the document-intelligence registry via
  `digitalmodel/specs/data-needs.yaml` as `NA-011`.
- Wrote explicit source-block evidence to
  `.claude/work-queue/assets/WRK-1381/evidence/source-asset-check.yaml`.
- Posted status updates to GitHub issue `#458`, including current blocker and next step.

### Current Blocker
- True source-backed `figure_digitized` execution is blocked because the expected
  source assets are not present in the active workspace snapshot:
  `PNA-GZ-Curves.manifest.yaml`, real `curves/index.jsonl`, and accessible
  PNA / Biran / EN400 GZ figure assets.

### Next Step
- Import or locate at least one real source figure/manifold asset, then add one
  true `figure_digitized` condition with `source_checkpoints` and
  `max_error_pct <= 2.0` to both:
  - `digitalmodel/tests/fixtures/test_vectors/naval_architecture/gz_curves.yaml`
  - `digitalmodel/data/doc-intelligence/digitized-curves/gz-curves.yaml`
- If source assets remain unavailable, treat the remaining digitization tranche as
  source-blocked and continue via a follow-up source-acquisition step.
