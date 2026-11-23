## Parent: #1668 (retroactive review)

## Problem
Codex adversarial review (2026-04-02) found schema mismatch:
- `submit-batch.sh` requires each job to have `solver` and `input_file`
- `validate_manifest.py` defines `name`, `solver_type`, and `model_file`

A manifest can pass validation and fail at submission, or submit successfully without matching the validator's schema. This is a workflow-breaking contract bug.

## Severity: HIGH (S1)

## Acceptance Criteria
- [ ] Single source of truth for manifest schema (shared YAML schema or Python dataclass)
- [ ] submit-batch.sh and validate_manifest.py use the same field names
- [ ] Tests verify schema agreement between validator and submitter
- [ ] batch-manifest.yaml.example matches the unified schema

## Source
Review: `scripts/review/results/2026-04-02T132222Z-retroactive-review-codex.md`