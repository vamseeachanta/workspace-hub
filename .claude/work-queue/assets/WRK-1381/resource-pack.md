# Resource Pack: WRK-1381

## Problem Context
`WRK-1381` targets GZ (righting arm) curve digitization for naval-architecture TDD.
The current `digitalmodel` repo already contains a dedicated GZ fixture file and test
module, but only three traced curve conditions are present. The WRK acceptance target
is at least ten traced GZ curves plus a reusable digitized-curve artifact.

## Relevant Documents/Data
- `digitalmodel/tests/fixtures/test_vectors/naval_architecture/gz_curves.yaml`
- `digitalmodel/tests/naval_architecture/test_gz_curves.py`
- `digitalmodel/tests/fixtures/test_vectors/naval_architecture/en400_stability.yaml`
- `digitalmodel/tests/naval_architecture/test_en400_worked_examples.py`
- `digitalmodel/src/digitalmodel/naval_architecture/stability.py`
- `.claude/work-queue/pending/WRK-1381.md`
- `digitalmodel` issue `#458`

## Constraints
- TDD is mandatory before implementation changes.
- Existing in-repo source coverage is textbook-derived and partially summarized; the
  referenced upstream source assets (`curves/index.jsonl`, `PNA-GZ-Curves.manifest.yaml`)
  are not present in the current workspace snapshot.
- New fixtures must preserve traceability by condition, source, and units.
- The existing `stability.gz_from_cross_curves()` API is imperial-only (`kn_ft`, `kg_ft`);
  current tests already mix imperial and metric labels in fixture data, so schema clarity
  is required before expansion.

## Assumptions
- Issue `#458` is the canonical coordination thread for this WRK.
- Stage 2 approval on GitHub is sufficient to create planning inputs, but not to begin
  implementation.
- The initial implementation path should expand from available in-repo textbook-derived
  values first, then branch only if additional source assets are surfaced.

## Open Questions
- Should the canonical fixture schema support both imperial and metric curves in one file,
  or should the curves be normalized to one unit system for test consumption?
- Does the missing shared artifact belong in `workspace-hub` only, or should `digitalmodel`
  mirror or consume it directly?
- Are additional GZ conditions expected to be fully digitized curves, or can traced curve
  families derived from existing KN tables/count variants satisfy the `>= 10` target?

## Domain Notes
- `GZ = KN - KG * sin(heel)` is already implemented in `digitalmodel`.
- Current repo coverage includes:
  - 3 dedicated GZ curve conditions in `gz_curves.yaml`
  - EN400 point examples for DDG-51 stability calculations
  - IMO intact stability checks in existing tests
- The largest current gap is not algorithmic support; it is fixture breadth and
  source-traceable curve data.
