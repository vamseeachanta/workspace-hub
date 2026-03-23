# WRK-1380: Ship Dimensions Phase 1 Plan

## Mission

Populate the ship-dimensions template for the first execution slice of 110 SNAME ship-plan PDFs, prioritizing capital ships and verifying a subset against Jane's Fighting Ships 2009-2010. This remains manual-curation work; automation is limited to queueing and validation support.

## Constraints

- Execution repo is `workspace-hub`, per `WRK-1380.target_repos`; this slice must not assume a mounted `digitalmodel` checkout.
- The canonical `generate-ship-dimension-template.py` location is not present in the currently mounted repos and must be recovered from the WRK-1339 Child E handoff or replaced deliberately before execution.
- The canonical output path for `ship-dimensions.yaml` is not yet confirmed in the current `workspace-hub` checkout and must be pinned before data entry starts.
- Execution must not invent schema keys or output paths.
- First implementation slice must stay within the current simple WRK bounds.

## Acceptance Criteria

- [ ] Execution remains in `workspace-hub`; no Stage 7 work is routed to an unmounted `digitalmodel` repo.
- [ ] Canonical generator source from WRK-1339 Child E is recovered or an explicit replacement path is approved before data entry starts.
- [ ] Canonical output path for `ship-dimensions.yaml` is confirmed before data entry starts.
- [ ] Template is generated without schema drift.
- [ ] At least 30 vessels have complete `loa`, `beam`, `draft`, `depth`, `displacement`, and `speed`.
- [ ] All capital ships (`BB`, `CV`, `CA`, `CB`) are populated.
- [ ] At least 5 vessels are cross-referenced against Jane's and marked `entry_status: verified`.
- [ ] Validation passes before commit.

## Scripts to Create

| Script | Purpose | Inputs | Outputs | Phase |
|--------|---------|--------|---------|-------|
| `scripts/ship-dimensions/build-priority-queue.py` | Order extraction work by vessel class | template YAML, class map | ordered queue file | Stage 7 (`workspace-hub`) |
| `scripts/ship-dimensions/validate-phase1.py` | Check Phase 1 thresholds deterministically | populated YAML | pass/fail report | Stage 7 (`workspace-hub`) |

## Plan

1. Resolve the WRK-1339 Child E handoff inside `workspace-hub`: locate the generator script or the already-generated template/output artifact and record the canonical paths.
2. If the generator handoff is still absent, stop and escalate rather than inventing a new schema or output location.
3. Generate the empty template in the confirmed canonical path and freeze the schema.
4. Build the extraction queue in `workspace-hub`: capital ships first, destroyers second, auxiliaries last.
5. Populate the required six dimensions from ship plans.
6. Verify at least five vessels against Jane's and mark them verified.
7. Run deterministic Phase 1 validation before commit.

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

### Dependency Resolution Gate

1. Check the mounted `workspace-hub` checkout for the WRK-1339 Child E generator or generated template artifact.
2. If found, record the exact script path and canonical `ship-dimensions.yaml` output path in the execution checkpoint.
3. If not found, stop Stage 7 and return a blocker rather than creating a substitute schema ad hoc.

## Tests

| Test | Type | Expected |
|------|------|----------|
| `dependency_gate_fails_when_generator_missing` | error | Stage 7 setup fails fast when neither the generator nor the generated template artifact can be located in `workspace-hub` |
| `validate_phase1_happy_path` | happy | Validator passes when >=30 entries are complete, all capital ships are complete, and >=5 entries are verified |
| `validate_phase1_threshold_failure` | error | Validator fails and reports the unmet threshold when completeness or verification count is too low |
| `build_priority_queue_orders_classes` | happy | Queue orders capital ships first, destroyers second, auxiliaries last |

## Open Dependencies

1. Recover the WRK-1339 Child E generator or generated template artifact inside `workspace-hub`.
2. Pin the canonical `ship-dimensions.yaml` path in the current `workspace-hub` checkout once the parent artifact is found.
