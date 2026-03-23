# WRK-1380: Ship Dimensions Phase 1 Plan

## Mission

Populate the ship-dimensions template for the first execution slice of 110 SNAME ship-plan PDFs, prioritizing capital ships and verifying a subset against Jane's Fighting Ships 2009-2010. This remains manual-curation work; automation is limited to queueing and validation support.

## Constraints

- The canonical `generate-ship-dimension-template.py` location is not yet confirmed in this workspace.
- The canonical output path for `ship-dimensions.yaml` is not yet confirmed in this workspace.
- Execution must not invent schema keys or output paths.
- First implementation slice must stay within the current simple WRK bounds.

## Acceptance Criteria

- [ ] Canonical generator and output path are confirmed before data entry starts.
- [ ] Template is generated without schema drift.
- [ ] At least 30 vessels have complete `loa`, `beam`, `draft`, `depth`, `displacement`, and `speed`.
- [ ] All capital ships (`BB`, `CV`, `CA`, `CB`) are populated.
- [ ] At least 5 vessels are cross-referenced against Jane's and marked `entry_status: verified`.
- [ ] Validation passes before commit.

## Scripts to Create

| Script | Purpose | Inputs | Outputs | Phase |
|--------|---------|--------|---------|-------|
| `scripts/ship-dimensions/build-priority-queue.py` | Order extraction work by vessel class | template YAML, class map | ordered queue file | Stage 6 |
| `scripts/ship-dimensions/validate-phase1.py` | Check Phase 1 thresholds deterministically | populated YAML | pass/fail report | Stage 6 |

## Plan

1. Confirm the generator path and canonical output path.
2. Generate the empty template and freeze the schema.
3. Build the extraction queue: capital ships first, destroyers second, auxiliaries last.
4. Populate the required six dimensions from ship plans.
5. Verify at least five vessels against Jane's and mark them verified.
6. Run deterministic Phase 1 validation before commit.

## Pseudocode

### Queue Builder

1. Load template entries and infer vessel class from key or metadata.
2. Sort by class priority: `BB/CV/CA/CB`, then `DD`, then all remaining vessels.
3. Emit a stable queue with vessel id, class, completion state, and verification flag.

### Phase 1 Validator

1. Load `ship-dimensions.yaml` and count entries with all six required fields.
2. Check that every capital ship entry is complete.
3. Count `entry_status: verified` entries and fail below the threshold of 5.

### Manual Extraction Loop

1. Open the next vessel plan from the ordered queue and read the six required dimensions.
2. Record values into the existing YAML schema, leaving unknown fields blank rather than inventing values.
3. Compare against Jane's when available and mark the entry verified if it matches.

## Tests

| Test | Type | Expected |
|------|------|----------|
| `validate_phase1_happy_path` | happy | Validator passes when >=30 entries are complete, all capital ships are complete, and >=5 entries are verified |
| `validate_phase1_threshold_failure` | error | Validator fails and reports the unmet threshold when completeness or verification count is too low |
| `build_priority_queue_orders_classes` | happy | Queue orders capital ships first, destroyers second, auxiliaries last |

## Open Dependencies

1. Confirm where `generate-ship-dimension-template.py` lives.
2. Confirm the canonical repository/path for `ship-dimensions.yaml`.
3. Confirm whether execution occurs entirely from `workspace-hub` or requires the mounted `digitalmodel` repo.
