# WRK-1358: Dedup Scan — digitalmodel & O&G-Standards

## Acceptance Criteria

- AC1: File-level dedup scan completed across data/standards/promoted/ and digitalmodel/
- AC2: Content-level overlap assessment documented (hardcoded constants vs CSV tables)
- AC3: Findings report written with actionable recommendations
- AC4: GitHub issue updated with results

## Pseudocode

1. Enumerate all files in data/standards/promoted/ by category
2. Enumerate document files in digitalmodel/docs/domains/ and digitalmodel/data/
3. Compare basenames for exact duplicates
4. Check for content-level overlap (embedded constants referencing same standard tables)
5. Document findings in evidence/resource-intelligence.yaml
6. Update GitHub issue with summary

## Test Plan

- T1: Verify resource-intelligence.yaml contains dedup_findings section
- T2: Verify exact_file_duplicates count is documented
- T3: Verify recommendations are actionable (each has id + description)

## Result Summary

**No file-level duplicates found.** The two stores serve different purposes:
- `data/standards/promoted/` — extracted CSV tables from PDF standards (10,681 files)
- `digitalmodel/docs/domains/` — markdown knowledge docs (781 files)
- `digitalmodel/src/` — Python code with embedded constants

Architecture is correct: workspace-hub owns shared data, digitalmodel consumes via relative paths.

## Confirmation

confirmed_by: vamsee
confirmed_at: 2026-03-25T05:15:00Z
decision: passed
