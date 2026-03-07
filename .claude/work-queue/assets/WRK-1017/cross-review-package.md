# WRK-1017 Implementation Cross-Review Package

## Summary

Stage 5 hard gate fix — enforce interactive planning review as a blocking gate before Stage 6 cross-review.

## Commits Since Plan Baseline (5e2679a0)

```
eaa49006 feat(WRK-1017): Phase 1A complete — bootstrap script + legacy exemptions
adeb639f feat(WRK-1017): Phase 1B — Stage 5 gate guards on cross-review, claim, close
5d7bd405 feat(WRK-1017): Phase 1B hardening — test harness, CI, pre-commit, contract alignment
11cf2cfb feat(WRK-1017): Phase 2 — Changes Since Stage 5 section in plan-final HTML
```

## Key Deliverables

### Phase 1A
- `scripts/work-queue/verify-gate-evidence.py`: `check_stage5_evidence_gate()` + `--stage5-check` CLI mode
- `scripts/work-queue/stage5-gate-config.yaml`: activation enum, human_authority_allowlist
- `specs/templates/stage5-evidence-contract.yaml`: cross-artifact invariants
- `specs/templates/stage5-migration-exemption-template.yaml`: legacy exemption schema
- `specs/templates/user-review-*-template.yaml`: 4 required artifact templates
- `scripts/agents/plan.sh`: Stage 5 gate guard added
- `scripts/work-queue/bootstrap-stage5-gate.sh`: dry-run inventory script
- 36 unit tests (12 new Stage 5 + 24 existing)

### Phase 1B
- `scripts/review/cross-review.sh`: guarded (`--wrk-id` param added, plan reviews blocked)
- `scripts/work-queue/claim-item.sh`: guarded (before quota check)
- `scripts/work-queue/close-item.sh`: guarded (after WRK file resolution)
- `scripts/agents/tests/test-plan-gate.sh`: 41 integration tests
- `scripts/work-queue/tests/test-user-review-evidence-writers.sh`: 23 regression tests
- `.github/workflows/baseline-check.yml`: Stage 5 gate tests added as CI step
- `scripts/hooks/pre-commit`: Stage 5 guard consistency check when entrypoints staged
- `work-queue-workflow/SKILL.md` v1.0.4, `workflow-gatepass/SKILL.md` v1.0.5: canonical checker referenced

### Phase 2
- `scripts/work-queue/generate-html-review.py`: `collect_changes_since_stage5()` + `render_changes_since_stage5()`
- `tests/unit/test_generate_html_review.py`: 8 new tests (incl. AC-21b fixture-backed delta test)

## Test Coverage

| Suite | Tests | Status |
|---|---|---|
| unit/test_verify_gate_evidence.py | 36 | PASS |
| unit/test_generate_html_review.py | 58 | PASS |
| integration/test-plan-gate.sh | 41 | PASS |
| integration/test-user-review-evidence-writers.sh | 23 | PASS |
| **Total** | **158** | **ALL PASS** |

## Gate Verification

- `verify-gate-evidence.py WRK-1017`: all gates PASS
- `bootstrap-stage5-gate.sh --dry-run`: decision=go
- All four entrypoints guarded and tested
