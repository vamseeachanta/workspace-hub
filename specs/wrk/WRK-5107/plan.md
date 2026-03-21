# WRK-5107: Purge HTML Gates from verify-gate-evidence.py

## Context

WRK-5104 replaced the HTML lifecycle with GitHub issues. `verify-gate-evidence.py` still enforces HTML-era artifact checks, blocking stage 14 for all WRKs using the new workflow. User decision: **replace entirely** (no backward compat). Old archived WRKs won't be re-archived — this is an intentional migration.

## Files to Modify

### 1. `scripts/work-queue/verify-gate-evidence.py` (primary)

**Remove HTML-era functions (by name, not line number):**
| Function / Gate | Action |
|----------|-------|
| `check_browser_open_elapsed_time()` | Remove entirely |
| `check_html_open_default_browser_gate()` | Replace with `check_github_issue_gate()` |
| `check_user_review_publish_gate()` | Remove entirely |
| `check_plan_publish_predates_approval()` | Remove entirely |
| HTML gate registry entries (`html_open_required`, browser elapsed, publish uniqueness, publish-before-approval) | Remove by gate key |

**Replace plan gate:**
| Gate | Change |
|------|--------|
| `check_plan_confirmation()` | Accept `spec_ref` from frontmatter; validate path exists (don't hardcode `plan.md`) |

**Tweak non-HTML gates:**
| Gate | Change |
|------|--------|
| Integrated test | `3-5` → `3+`; count **unique** test refs only; int cast in try/except |
| Agent log | Optional when no multi-agent evidence exists; if multi-agent metadata present but logs missing → fail |
| Stage evidence | Accept `stage_evidence_ref` (already does); handle missing/malformed gracefully |
| Resource-intelligence | Add `"complete"` and `"done"`; **case-insensitive** normalization; unknown status → fail |
| Future-work | Accept both strings and objects with `disposition`; reject malformed (null, numbers, empty strings, empty dicts) |

**Add new gate:**
- `check_github_issue_gate()`: regex-only validation, **no network/gh dependency**
- Accept: `^https://(?:www\.)?github\.com/[^/]+/[^/]+/issues/\d+$`
- Reject: PR URLs, issue comment URLs, non-GitHub URLs, malformed issue numbers
- Error message: "github_issue_ref required (replaces retired HTML gate)"

### 2. `scripts/work-queue/gate_checks_archive.py`
- Replace `html_verification_ref` with `github_issue_ref` in `_REQUIRED_FIELDS`
- Replace file-path validation with same regex as `check_github_issue_gate()`
- Intentional migration: old archived WRKs with HTML fields won't pass if re-archived

### 3. `scripts/work-queue/audit-session-signal-coverage.py`
- Remove HTML signal entries from `REQUIRED_SIGNALS`
- Remove HTML branch from `_session_infers_signal()`
- Keep tolerant of historical session data (don't crash on retired signals)

### 4. `scripts/work-queue/build-session-gate-analysis.py`
- Remove HTML signal definitions and gate keys
- Keep historical input parsing tolerant

### 5. `scripts/work-queue/backfill-categories.py`
- Remove HTML category regex pattern

### 6. `scripts/work-queue/process.md` (already done)

## Implementation Order

1. **Tests first** — write/adjust tests for all gate changes before touching implementation
2. **verify-gate-evidence.py** — remove HTML functions, add `check_github_issue_gate()`, tweak gates
3. **gate_checks_archive.py** — swap field and validation
4. **audit-session-signal-coverage.py** — remove HTML signals
5. **build-session-gate-analysis.py** — remove HTML signals
6. **backfill-categories.py** — remove HTML regex
7. **End-to-end verification**

## Test Plan

Use `@pytest.mark.parametrize` for boundary conditions.

| Test | Type | Expected |
|------|------|----------|
| Verifier on WRK-5104 assets | Happy path | All gates pass |
| WRK with valid `github_issue_ref`, no HTML artifacts | Happy path | Pass |
| WRK missing `github_issue_ref` | Error path | Fail with clear message |
| Malformed `github_issue_ref` (local path, invalid URL) | Error path | Fail |
| PR URL instead of issue URL | Error path | Fail |
| Issue comment URL | Error path | Fail |
| Integrated test count = 2 unique refs | Edge | Fail |
| Integrated test count = 3 unique refs | Edge | Pass |
| Integrated test count = 10 unique refs | Edge | Pass |
| Duplicates totaling 3 but only 2 unique refs | Edge | Fail |
| Future-work with simple strings | Edge | Pass |
| Future-work with mixed string + object | Edge | Pass |
| Future-work with malformed entry (null, number, empty) | Edge | Fail clearly |
| Resource-intelligence `completion_status: done` | Edge | Pass |
| Resource-intelligence `completion_status: COMPLETE` | Edge | Pass (case-insensitive) |
| Resource-intelligence unknown status | Error path | Fail |
| Single-agent WRK with no agent logs | Edge | Pass |
| Multi-agent WRK missing agent logs | Edge | Fail |
| `spec_ref` present and valid | Happy path | Plan gate passes |
| `spec_ref` missing | Error path | Plan gate fails clearly |
| `gate_checks_archive.py` with valid URL | Happy path | Pass |
| Stage 14 pre-exit hook end-to-end | Integration | Full pipeline passes |
| No network calls during execution | Reliability | Zero network egress |

## Verification

```bash
# Targeted tests first
uv run --no-project python -m pytest scripts/work-queue/tests -k "gate_evidence or gate_checks_archive" -v

# Verifier against WRK-5104
uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-5104 --phase close

# Stage 14 integration
bash scripts/work-queue/exit_stage.py WRK-5104 14

# Full regression
uv run --no-project python -m pytest scripts/work-queue/tests -v
```

## Synthesis Notes

Merged from 3-agent review (Claude, Codex, Gemini):
- **Codex**: tests-first order, unique test refs, no network for GitHub validation, explicit archive migration decision, `uv run --no-project`, agent-log optionality by evidence not count
- **Gemini**: regex URL validation, case-insensitive status, parameterized pytest, defensive file I/O, zero network egress test
- **Claude**: baseline structure, implementation scope, file identification
