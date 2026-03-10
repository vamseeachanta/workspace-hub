# WRK-668 Plan — Codex Review

_Note: Codex quota exhausted; Claude Opus fallback used per submit-to-codex.sh policy._

## Assessment

Plan is actionable and deterministic. Each deliverable has clear file targets and
machine-verifiable exit criteria.

The dependency ordering is correct: schema-first → TDD → implementation → HTML card →
shell hardening ensures each layer has a stable contract from the layer below.

Risk: `verify-gate-evidence.py` is large (~2100 lines). Recommend isolating
`check_archive_readiness()` in `gate_checks_archive.py` (matching the existing pattern
from `gate_checks_extra.py`) rather than inlining. This keeps the main verifier's line
count within bounds and makes the new check independently testable.

The spin-off script approach (accept blocker description, call next-id.sh, scaffold WRK)
is the correct pattern — avoids baking blocker classification logic into the verifier.

## Verdict: APPROVE_WITH_MINOR

Minor: extract `check_archive_readiness()` to `gate_checks_archive.py`. Otherwise
implementation scope is tight and unambiguous.
