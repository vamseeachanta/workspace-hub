# WRK-1380 Plan: Ship Dimensions Phase 1

## Context

`WRK-1380` is a manual-curation child of `WRK-1339`. The job is to populate a ship-dimensions template for 110 SNAME ship-plan PDFs, complete a Phase 1 subset first, and verify a sample against Jane's Fighting Ships 2009-2010.

Current planning dependency: the named template generator (`generate-ship-dimension-template.py`) and the canonical output location for `ship-dimensions.yaml` are still not discoverable in the mounted `workspace-hub` checkout. Execution cannot assume those paths until the WRK-1339 Child E handoff is recovered locally.

## Chunk Sizing Check

- `max_repos: 1` -> within limit
- `max_files_changed: 5` -> plan assumes <=5 implementation files in the first execution slice
- `max_plan_words: 150` -> execution plan below kept compact
- `max_test_modules: 1` -> one validation test module/script in first slice

Result: stay in the current WRK; no feature split required at Stage 4.

## Scripts To Create

The manual extraction itself should remain human-driven, but the surrounding validation and queue-building steps are likely reusable across future ship-plan batches.

1. `scripts/ship-dimensions/build-priority-queue.py`
- Inputs: template YAML, vessel-class priority map
- Outputs: ordered extraction queue (`csv` or `md`)
- Creation phase: Stage 6 implementation

2. `scripts/ship-dimensions/validate-phase1.py`
- Inputs: populated `ship-dimensions.yaml`
- Outputs: AC report for completeness, capital-ship coverage, and Jane's verification count
- Creation phase: Stage 6 implementation

## Acceptance Criteria

1. A confirmed template is generated from the canonical generator without hand-editing schema keys.
2. At least 30 vessels have complete values for `loa`, `beam`, `draft`, `depth`, `displacement`, and `speed`.
3. All capital ships in scope (`BB`, `CV`, `CA`, `CB`) are populated.
4. At least 5 populated vessels are cross-checked against Jane's and marked `entry_status: verified`.
5. Validation output shows Phase 1 thresholds met before commit.

## Execution Plan

1. Confirm generator path and output YAML path.
2. Generate the empty template and freeze the schema.
3. Build a priority queue for capital ships, then destroyers, then auxiliaries.
4. Populate vessel dimensions from ship plans with source notes.
5. Verify at least five entries against Jane's and set `entry_status: verified`.
6. Run Phase 1 validation before commit.

## Pseudocode

### Queue Builder

1. Load the template entries and derive each vessel class from its key or metadata.
2. Sort entries by class priority: `BB/CV/CA/CB`, then `DD`, then remaining auxiliaries.
3. Emit a stable work queue with vessel id, class, status, and verification-needed flag.

### Phase 1 Validator

1. Load `ship-dimensions.yaml` and count entries with all required fields present.
2. Check that every capital ship entry is complete.
3. Count entries marked `entry_status: verified` and fail if the count is below 5.

### Manual Extraction Loop

1. Open the next ship plan from the priority queue and capture the six required dimensions.
2. Record the values in the YAML using the existing schema and leave blank fields untouched when data is unavailable.
3. If Jane's is available for that vessel, compare the values and mark the entry as verified.

## Test Plan

1. `validate-phase1 happy path`
- Case: populated YAML with >=30 complete entries, all capital ships complete, >=5 verified
- Expected: validator exits success and reports all ACs satisfied

2. `validate-phase1 threshold failure`
- Case: 29 complete entries or fewer than 5 verified entries
- Expected: validator exits failure and identifies the failed threshold

3. `queue ordering`
- Case: mixed vessel classes in template
- Expected: queue output orders capital ships first, destroyers second, auxiliaries last

## Official API / Scraper Check

No scraper or estimator is planned for this WRK. Stage 4 uses local files and mounted references only.

## Open Dependencies

1. Recover the WRK-1339 Child E generator or generated template artifact inside `workspace-hub`.
2. Confirm the canonical repository/path for the generated `ship-dimensions.yaml` within `workspace-hub`.
3. Keep Phase 1 execution in `workspace-hub`, consistent with `WRK-1380.target_repos`.
