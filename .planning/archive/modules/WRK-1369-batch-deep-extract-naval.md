# WRK-1369: Batch Deep Extraction — Naval Architecture

## Mission
Execute batch-deep-extract-naval.sh on all textbook manifests, verify results, rebuild indexes, report yield.

## Acceptance Criteria
1. Extraction reports exist for all textbook manifests (44 of 44)
2. Total deep-extracted worked examples >= 100 (target: 150-200)
3. JSONL indexes rebuilt with deep records preferred
4. Yield report written to data/doc-intelligence/extraction-yield-report.yaml

## Pseudocode
1. Run batch-deep-extract-naval.sh (skips existing reports)
2. Count extraction reports vs manifest count
3. Aggregate worked_examples from all reports
4. Run assess-extraction-quality.py --report
5. Run build-doc-intelligence.py --force to rebuild JSONL indexes
6. Write extraction-yield-report.yaml with actual vs target comparison

## Test Plan
| What | Type | Expected |
|------|------|----------|
| All textbook manifests have reports | Happy path | 44/44 reports exist |
| Worked example count meets threshold | Happy path | >= 100 examples |
| JSONL rebuild completes without error | Happy path | Exit 0, indexes updated |
| Yield report YAML is valid | Edge case | parseable YAML with all required fields |

## Scripts to Create
None — all scripts already exist (batch-deep-extract-naval.sh, assess-extraction-quality.py, build-doc-intelligence.py). Fix needed: add PEP 723 metadata to build-doc-intelligence.py.

## Plan Confirmation
confirmed_by: vamsee
confirmed_at: 2026-03-24T02:55:00Z
decision: passed
