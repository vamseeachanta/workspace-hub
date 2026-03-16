---
name: work-queue-cross-review-route-bc
description: 'Sub-skill of work-queue: Cross-Review (Route B/C).'
version: 1.8.0
category: coordination
type: reference
scripts_exempt: true
---

# Cross-Review (Route B/C)

## Cross-Review (Route B/C)


After each implementation phase:
1. Write `scripts/review/results/wrk-NNN-phase-N-review-input.md`
2. Submit: `scripts/review/cross-review.sh <file> all` (Codex is hard gate)
3. Collect verdicts: APPROVE / MINOR / MAJOR
4. Fix MAJOR findings before next phase; document deferred MINORs

Codex: `scripts/review/submit-to-codex.sh --file <path>`
Gemini: `scripts/review/submit-to-gemini.sh --file <path>`

Maximum 3 iterations per WRK. Enforced by `review-iteration.yaml` in assets.
After 3 passes `cross-review.sh` exits 1 — resolve findings and close the WRK.
