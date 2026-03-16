---
name: workflow-gatepass-close-gate-minimum
description: 'Sub-skill of workflow-gatepass: Close Gate Minimum.'
version: 1.0.6
category: workspace-hub
type: reference
scripts_exempt: true
---

# Close Gate Minimum

## Close Gate Minimum


Before close, require all of:

- `plan gate` passed
- `TDD gate` passed
- `integrated test gate` passed (3-5 pass records)
- `legal gate` passed
- `cross-review gate` passed (R-28: iteration count ≤ 3, verified via `review-iteration.yaml`)
- `user-review html-open gate` passed for each user-review checkpoint
- `user-review publish gate` passed for each user-review checkpoint
- `resource-intelligence gate` passed
- `reclaim gate` evaluated (pass or n/a with reason)
- `future-work gate` passed
- `archive-readiness gate` passed or deferred with follow-up WRK
- `stage evidence gate` passed (`stage_evidence_ref` file exists and includes stages 1-20)
