Follow-up validation hardening after reviewing the latest provider-audit hotspot chain:

- Re-checked the recent claude hotspot pointing at `scripts/review/submit-to-codex.sh`
- Current assessment: the stdin-inheritance fix itself still looks sound; no new wrapper-path change is justified from the latest logs
- Added regression coverage for the two remaining meaningful failure classes around dispatch diagnostics:
  - `T30`: timeout classification keeps exit `124` and emits timeout guidance
  - `T31`: transport classification keeps exit `1` and emits transport/network guidance
- Re-ran the full shell suite:
  - `bash tests/review/test-submit-scripts.sh`
  - result: 59 passed, 0 failed

Net: #2406 now has stronger protection not just against the original stdin hang, but also against silent regressions in timeout/transport failure handling.