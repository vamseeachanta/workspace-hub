# WRK-5107: Purge HTML Gates from verify-gate-evidence.py

## Context

WRK-5104 replaced the HTML lifecycle with GitHub issues. `verify-gate-evidence.py` still enforces HTML-era artifact checks, blocking stage 14 for all WRKs using the new workflow. User decision: **replace entirely** (no backward compat).

## Files to Modify

### 1. `scripts/work-queue/verify-gate-evidence.py` (primary — ~1960 lines)

**Remove these HTML-era functions:**
| Function | Lines | Replacement |
|----------|-------|-------------|
| `check_browser_open_elapsed_time()` | 600-676 | Remove entirely |
| `check_html_open_default_browser_gate()` | 1300-1333 | Replace with `check_github_issue_gate()` — verify `github_issue_ref` in frontmatter |
| `check_user_review_publish_gate()` | 1336-1372 | Remove — GitHub issue update replaces publish |
| `check_plan_confirmation()` | 1459-1478 | Replace: accept `spec_ref` → plan.md instead of `plan_html_review_final_ref` |
| `check_plan_publish_predates_approval()` | 927-982 | Remove — no longer applicable |

**Remove from gate registry (lines 1830-1836):**
- `html_open_required` list and its usage
- Registration of HTML gates at lines 1833-1836
- Browser elapsed time gate at lines 1894-1895
- Publish commit uniqueness gate at lines 1920-1921
- Plan publish predates approval gate at lines 1932-1933

**Remove from plan gate (line 1785):**
- `plan_html_review_final_ref` field handling → replace with `spec_ref`

**Tweak non-HTML gates:**
| Gate | Lines | Change |
|------|-------|--------|
| Integrated test | 1425-1456 | `3-5` → `3+` (remove upper bound at line 1439) |
| Agent log | 1689-1755 | Make optional: skip if single-agent (check log count) |
| Stage evidence | 1481-1538 | Accept `stage_evidence_ref` from frontmatter (already does) |
| Resource-intelligence | 1165-1199 | Add `"complete"` and `"done"` to valid `completion_status` values |
| Future-work | 1202-1255 | Accept simple strings in `recommendations` list (not just objects with `disposition`) |

**Add new gate:**
- `check_github_issue_gate()`: verify `github_issue_ref` in WRK frontmatter resolves to a valid GitHub issue URL

### 2. `scripts/work-queue/audit-session-signal-coverage.py`
- Remove lines 15, 16, 18: HTML signal entries from `REQUIRED_SIGNALS`
- Remove lines 75-76: `_session_infers_signal()` HTML branch
- Low risk — diagnostic only

### 3. `scripts/work-queue/build-session-gate-analysis.py`
- Remove lines 55-57: HTML signal definitions
- Remove lines 198-200: HTML gate keys
- Low risk — diagnostic only

### 4. `scripts/work-queue/backfill-categories.py`
- Remove line 32: HTML category regex pattern
- Low risk — metadata only

### 5. `scripts/work-queue/gate_checks_archive.py`
- Line 28: Replace `html_verification_ref` with `github_issue_ref` in `_REQUIRED_FIELDS`
- Lines 79-86: Update validation to check URL format instead of file path
- **High risk** — hard gate, must replace not just remove

### 6. `scripts/work-queue/process.md` (already done)
- 3 locations: `3-5` → `3+` ✅

## Implementation Order

1. **verify-gate-evidence.py** — remove HTML functions, add `check_github_issue_gate()`, tweak 5 gates
2. **gate_checks_archive.py** — swap `html_verification_ref` → `github_issue_ref`
3. **audit-session-signal-coverage.py** — remove HTML signals
4. **build-session-gate-analysis.py** — remove HTML signals
5. **backfill-categories.py** — remove HTML regex

## Test Plan

| Test | Type | Expected |
|------|------|----------|
| Run `verify-gate-evidence.py` against WRK-5104 assets | Happy path | All gates pass |
| Run against a WRK with `github_issue_ref` but no HTML artifacts | Happy path | Pass |
| Run against a WRK missing `github_issue_ref` | Error path | Fail with clear message |
| Integrated test count = 3 | Edge | Pass (was fail before) |
| Integrated test count = 10 | Edge | Pass (no upper limit) |
| Future-work with simple string recommendations | Edge | Pass |
| Resource-intelligence with `completion_status: done` | Edge | Pass |
| `gate_checks_archive.py` with `github_issue_ref` URL | Happy path | Archive gate passes |
| Stage 14 pre_exit_hook end-to-end | Integration | Full pipeline passes |

## Verification

```bash
# Unit: run verifier against WRK-5104
python scripts/work-queue/verify-gate-evidence.py WRK-5104 --phase close

# Integration: stage 14 exit hook
bash scripts/work-queue/exit_stage.py WRK-5104 14

# Regression: run existing tests
python -m pytest scripts/work-queue/tests/ -v
```
