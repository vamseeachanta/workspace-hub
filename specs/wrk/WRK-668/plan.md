# WRK-668 Plan: Archive Tooling Contract and Auto Spin-off Workflow

**Route**: B | **Complexity**: medium | **Priority**: high
**Approved**: pending Stage 5 user review

## Context

WRK-624 gap review returned `archive: revise` — the current archive stage has stub merge/sync gates,
no canonical evidence schema, no archive-specific gate phase in the verifier, no spin-off automation,
and no HTML readiness card. This plan closes all 7 identified gaps (GAP-A through GAP-G).

## Deliverables

1. **Archive evidence schema** — `scripts/work-queue/templates/archive-tooling-template.yaml`
   - Required fields: `merge_status`, `sync_status`, `html_verification_ref`, `legal_scan_ref`,
     `document_index_ref`, `archive_readiness` (pass|soft-fail|hard-fail)
   - Optional: `spin_off_wrks[]` list

2. **TDD test suite** (written BEFORE implementation) — `scripts/work-queue/tests/test_archive_readiness.py`
   - T1: `test_archive_pass` — all gates satisfied → `(True, ...)`
   - T2: `test_archive_soft_fail_workaround` — document-index absent with exemption note → `(None, ...)`
   - T3: `test_archive_hard_fail_spinoff` — merge_status sentinel detected → `(False, ...)`

3. **`check_archive_readiness()` + `--phase archive`** in `verify-gate-evidence.py`
   - Validates `archive-tooling.yaml` exists and has required fields non-sentinel
   - Wire into `run_checks()` under `phase == "archive"`
   - `archive-item.sh` updated to call `--phase archive` (not `--phase close`)

4. **`create-spinoff-wrk.sh`** — `scripts/work-queue/create-spinoff-wrk.sh`
   - Args: `<source-WRK> <blocker-description> [--owner <provider>] [--workstation <machine>]`
   - Calls `next-id.sh`, scaffolds `pending/WRK-NNN.md`, records spin-off in `archive-tooling.yaml`

5. **HTML Archive Readiness card** in `generate-html-review.py`
   - Extend stage 20 block to render pass/fail badges per gate
   - Spin-off table when `spin_off_wrks` populated

6. **Harden `archive-item.sh`**
   - Replace stub merge/sync lines with real checks (git status clean + remote in sync)
   - Stage 20 evidence update promoted from best-effort to hard gate

## Strategy

- TDD: 3 scenario tests written first (T1-T3), all RED before any implementation
- Run: `uv run --no-project python -m pytest scripts/work-queue/tests/test_archive_readiness.py -v`
- Existing gate verifier tests must remain GREEN throughout

## Sequence

```
T1-T3 tests (RED) →
  archive-tooling schema →
  check_archive_readiness() (T1-T3 GREEN) →
  create-spinoff-wrk.sh →
  HTML card →
  archive-item.sh hardening →
  full test suite green →
  cross-review (Claude + Codex + Gemini)
```

## Tests / Evals

| # | Test | File | Expected |
|---|------|------|----------|
| T1 | `test_archive_pass` — all gates satisfied | `scripts/work-queue/tests/test_archive_readiness.py` | `(True, ...)` |
| T2 | `test_archive_soft_fail_workaround` — document-index absent with exemption | `scripts/work-queue/tests/test_archive_readiness.py` | `(None, ...)` |
| T3 | `test_archive_hard_fail_spinoff` — merge_status sentinel detected | `scripts/work-queue/tests/test_archive_readiness.py` | `(False, ...)` |
| T4 | Existing verifier tests remain GREEN after changes | `scripts/work-queue/tests/test_gate_verifier_hardening.py` | All PASS |

## Out of Scope

- Changes to close-item.sh logic (already complete)
- Document-index hook implementation (existing infrastructure)
- Changes to claim or triage stages
