OpenAI Codex v0.115.0 (research preview)
--------
workdir: /mnt/local-analysis/workspace-hub
model: gpt-5.4
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR, /home/vamsee/.codex/memories]
reasoning effort: medium
reasoning summaries: none
session id: 019d0fd7-3220-7410-b4a8-822115c52eea
--------
user
# Stance: Codex Plan Draft Review

You are a software engineer agent. Your focus is on **implementation correctness, edge cases, and testability**.

You will receive a Claude-authored plan draft. Walk it section-by-section and produce your own refined version.

When reviewing:
1. Challenge any assumptions about implementation approach — is there a simpler or more robust way?
2. Identify edge cases not covered (malformed input, missing fields, timezone/date math, quota exhaustion).
3. Flag AC gaps — things implementable but not covered by the listed tests.
4. Assess integration risks (nightly cron, file writes, CLI availability).
5. Verify uv run --no-project python is used wherever Python is called.

Your output must be a complete refined plan (same structure as the input draft).
Add a "Codex Notes" section at the end with your specific findings.

---
CLAUDE DRAFT PLAN:
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
warning: Ignoring malformed agent role definition: failed to deserialize agent role file at /mnt/local-analysis/workspace-hub/.codex/agents/batch/config.toml: invalid type: string "Read(*)", expected struct FilesystemPermissionsToml

warning: Ignoring malformed agent role definition: failed to deserialize agent role file at /mnt/local-analysis/workspace-hub/.codex/agents/explorer/config.toml: invalid type: string "Read(*)", expected struct FilesystemPermissionsToml

warning: Ignoring malformed agent role definition: failed to deserialize agent role file at /mnt/local-analysis/workspace-hub/.codex/agents/worker/config.toml: invalid type: string "Read(*)", expected struct FilesystemPermissionsToml

mcp startup: no servers
codex
Reviewing the draft against the actual gate scripts now. I’m checking the referenced functions, current field names, and whether the proposed tests cover the real failure modes before I rewrite the plan.
codex
The shell wrapper is failing in this workspace, so I’m falling back to direct file reads through simpler commands. I only need enough source context to validate the draft’s assumptions and tighten the plan.
codex
# WRK-5107: Purge HTML Gates from `verify-gate-evidence.py`

## Context

WRK-5104 replaced the HTML lifecycle with GitHub issues. `verify-gate-evidence.py` still enforces HTML-era artifact checks, blocking stage 14 for WRKs on the new workflow. User decision: **replace entirely** for active workflow enforcement.

One implementation correction to carry through the whole plan: do not make this a line-number-driven edit. Remove/replace gates by function name and gate key so the change is resilient to file drift.

## Files to Modify

### 1. `scripts/work-queue/verify-gate-evidence.py` (primary)

**Remove these HTML-era functions and registrations:**
| Function / Gate | Action | Notes |
|----------|-------|-------------|
| `check_browser_open_elapsed_time()` | Remove entirely | No HTML/browser lifecycle remains |
| `check_html_open_default_browser_gate()` | Replace with `check_github_issue_gate()` | New gate should validate `github_issue_ref` from frontmatter |
| `check_user_review_publish_gate()` | Remove entirely | “publish” no longer exists in GitHub-issue workflow |
| `check_plan_publish_predates_approval()` | Remove entirely | HTML publish chronology is obsolete |
| HTML gate registry entries (`html_open_required`, browser elapsed, publish uniqueness, publish-before-approval) | Remove entirely | Delete by gate key, not by line number |

**Replace plan gate behavior:**
| Gate | Change | Notes |
|------|-------|-------|
| `check_plan_confirmation()` | Replace HTML artifact dependency with plan evidence based on `spec_ref` | Do not assume every valid plan is an HTML artifact |

Plan-gate refinement:
- Prefer `spec_ref` when present and validate it points to a real plan artifact.
- Do not hardcode only `plan.md` unless that is already a workspace rule for this route.
- If Route A/B permits plan content in the WRK body, confirm the gate logic does not accidentally fail those WRKs. If this verifier is only for Route C/file-backed plans, state that explicitly in code and test it.

**Tweak non-HTML gates:**
| Gate | Change | Notes |
|------|-------|-------|
| Integrated test gate | `3-5` → `3+` | Count unique integrated-test refs only; no upper bound |
| Agent log gate | Make optional for single-agent runs | Do not infer “single-agent” from raw log count alone unless that is how the current schema encodes it |
| Stage evidence gate | Keep accepting `stage_evidence_ref` | Add malformed/missing-type handling if absent today |
| Resource-intelligence gate | Accept `"complete"` and `"done"` | Normalize case/whitespace before comparison |
| Future-work gate | Accept simple strings in `recommendations` | Continue accepting object entries too |

Agent-log refinement:
- Skip only when multi-agent execution is not evidenced anywhere.
- If `agent_logs` is present, validate shape and contents even for a single entry.
- If multi-agent metadata exists but logs are missing, still fail.

Future-work refinement:
- Accept both:
  - string entries
  - object entries with `disposition`
- Reject malformed entries like numbers, empty dicts, or blank strings with a clear error.

Resource-intelligence refinement:
- Normalize status values case-insensitively.
- Preserve failure for unknown statuses after normalization.

**Add new gate:**
- `check_github_issue_gate()`
- Validate `github_issue_ref` locally without network or `gh` dependency.
- Accept canonical GitHub issue URLs with optional trailing slash/query string.
- Reject:
  - PR URLs
  - issue comment URLs
  - non-GitHub URLs
  - malformed issue numbers
- Error message should say this is a required replacement for the retired HTML gate.

### 2. `scripts/work-queue/audit-session-signal-coverage.py`

- Remove HTML-only entries from `REQUIRED_SIGNALS`.
- Remove HTML-only inference branches from `_session_infers_signal()`.
- Keep the script tolerant of historical session data if it may still parse older records; it should stop requiring HTML, not crash on seeing it.

### 3. `scripts/work-queue/build-session-gate-analysis.py`

- Remove HTML-only signal definitions and gate keys from current analysis output.
- Keep historical input parsing tolerant if archived data may still contain retired gate names.

### 4. `scripts/work-queue/backfill-categories.py`

- Remove the HTML category regex only if this script is meant to stop classifying historical HTML-era records too.
- If the script still scans old archives, prefer making HTML classification non-required/non-emitted for new records rather than breaking historical backfills unintentionally.

### 5. `scripts/work-queue/gate_checks_archive.py`

- Replace `html_verification_ref` with `github_issue_ref` in `_REQUIRED_FIELDS`.
- Replace file-path validation with local GitHub issue URL validation.
- Decide explicitly whether archived pre-WRK-5104 items are now expected to fail.
  - If yes, document that this is an intentional archive-breaking migration.
  - If no, add a cutover rule or migration path for historical archives.

This is the highest integration risk outside the main verifier because it is itself a hard gate.

### 6. `scripts/work-queue/process.md` (already done)

- `3-5` → `3+` already updated.
- During verification, confirm script behavior matches doc wording so the repo does not drift again.

## Implementation Order

1. **Add/adjust tests first**
   - Add targeted tests for retired HTML gates, new GitHub issue validation, `3+` integrated tests, agent-log optionality, status normalization, and mixed recommendation shapes.
2. **`verify-gate-evidence.py`**
   - Remove HTML-only checks and registrations by gate key/name.
   - Add `check_github_issue_gate()`.
   - Update plan, integrated-test, agent-log, resource-intelligence, and future-work logic.
3. **`gate_checks_archive.py`**
   - Swap archive-required field and validation semantics.
   - Decide and encode historical archive behavior explicitly.
4. **`audit-session-signal-coverage.py`**
   - Remove HTML requirements.
5. **`build-session-gate-analysis.py`**
   - Remove HTML reporting keys.
6. **`backfill-categories.py`**
   - Remove or demote HTML classification only after confirming historical-data intent.
7. **End-to-end verification**
   - Re-run close/stage-14 flow on a GitHub-issue-based WRK.

## Test Plan

| Test | Type | Expected |
|------|------|----------|
| Verifier on WRK-5104 GitHub-issue workflow assets | Happy path | Passes without any HTML artifacts |
| WRK with valid `github_issue_ref` and no HTML fields | Happy path | Passes |
| WRK missing `github_issue_ref` | Error path | Fails with clear replacement message |
| WRK with malformed `github_issue_ref` (`issues/foo`) | Error path | Fails |
| WRK with PR URL instead of issue URL | Error path | Fails |
| WRK with issue comment URL instead of issue URL | Error path | Fails |
| Integrated test count = 2 unique refs | Edge | Fails |
| Integrated test count = 3 unique refs | Edge | Passes |
| Integrated test count = 10 unique refs | Edge | Passes |
| Integrated test list with duplicates totaling 3 but only 2 unique refs | Edge | Fails |
| Future-work with simple string recommendations | Edge | Passes |
| Future-work with mixed string + object recommendations | Edge | Passes |
| Future-work with malformed recommendation entry (`null`, number, empty string) | Edge | Fails clearly |
| Resource-intelligence `completion_status: done` | Edge | Passes |
| Resource-intelligence `completion_status: COMPLETE` | Edge | Passes if normalized |
| Resource-intelligence unknown status | Error path | Fails |
| Single-agent WRK with no agent logs | Edge | Passes if no multi-agent evidence exists |
| Multi-agent WRK missing agent logs | Edge | Fails |
| `spec_ref` present and valid | Happy path | Plan gate passes |
| `spec_ref` missing where required by route | Error path | Plan gate fails clearly |
| `gate_checks_archive.py` with valid `github_issue_ref` URL | Happy path | Passes |
| `gate_checks_archive.py` against historical HTML-era record | Regression/decision test | Behavior matches explicit migration decision |
| Stage 14 pre-exit hook end-to-end | Integration | Full pipeline passes |
| Diagnostic scripts on historical data containing retired HTML signals | Integration | No crash; expected output reflects retired gates |

## Verification

```bash
# Targeted verifier run
uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-5104 --phase close

# Archive gate validation
uv run --no-project python scripts/work-queue/gate_checks_archive.py

# Stage 14 integration
bash scripts/work-queue/exit_stage.py WRK-5104 14

# Regression tests
uv run --no-project python -m pytest scripts/work-queue/tests -v

# If there is a dedicated test file for these gates, run it first for faster feedback
uv run --no-project python -m pytest scripts/work-queue/tests -k "gate_evidence or gate_checks_archive" -v
```

## Codex Notes

- The draft assumes `spec_ref` always replaces `plan_html_review_final_ref`, but that may be wrong if Route A/B plans can live in the WRK body instead of a file. That needs an explicit rule before implementation.
- `check_github_issue_gate()` should not depend on `gh`, network access, or live GitHub resolution. URL-shape validation is the robust option here.
- “Make agent log optional: skip if single-agent (check log count)” is underspecified and risky. Optionality should be driven by workflow evidence, not just how many logs happen to exist.
- The integrated-test change needs uniqueness semantics; otherwise duplicate refs can satisfy `3+` incorrectly.
- The archive-script change is an AC gap in the original draft. If older archived WRKs still use HTML-era fields, this plan must explicitly choose between breaking them or supporting a cutover rule.
- The diagnostic-script removals are called “low risk,” but they can still break nightly cron/reporting if historical data contains retired signals. Keep parsing tolerant even if requirements are removed.
- The draft’s verification commands used bare `python`; they should be `uv run --no-project python ...` throughout, including pytest invocations.
- I could not inspect the live source in this session because shell execution in the workspace is currently failing under sandbox startup, so the refinement above is based on the draft plus workspace policy constraints rather than direct code confirmation.
tokens used
122,500
# WRK-5107: Purge HTML Gates from `verify-gate-evidence.py`

## Context

WRK-5104 replaced the HTML lifecycle with GitHub issues. `verify-gate-evidence.py` still enforces HTML-era artifact checks, blocking stage 14 for WRKs on the new workflow. User decision: **replace entirely** for active workflow enforcement.

One implementation correction to carry through the whole plan: do not make this a line-number-driven edit. Remove/replace gates by function name and gate key so the change is resilient to file drift.

## Files to Modify

### 1. `scripts/work-queue/verify-gate-evidence.py` (primary)

**Remove these HTML-era functions and registrations:**
| Function / Gate | Action | Notes |
|----------|-------|-------------|
| `check_browser_open_elapsed_time()` | Remove entirely | No HTML/browser lifecycle remains |
| `check_html_open_default_browser_gate()` | Replace with `check_github_issue_gate()` | New gate should validate `github_issue_ref` from frontmatter |
| `check_user_review_publish_gate()` | Remove entirely | “publish” no longer exists in GitHub-issue workflow |
| `check_plan_publish_predates_approval()` | Remove entirely | HTML publish chronology is obsolete |
| HTML gate registry entries (`html_open_required`, browser elapsed, publish uniqueness, publish-before-approval) | Remove entirely | Delete by gate key, not by line number |

**Replace plan gate behavior:**
| Gate | Change | Notes |
|------|-------|-------|
| `check_plan_confirmation()` | Replace HTML artifact dependency with plan evidence based on `spec_ref` | Do not assume every valid plan is an HTML artifact |

Plan-gate refinement:
- Prefer `spec_ref` when present and validate it points to a real plan artifact.
- Do not hardcode only `plan.md` unless that is already a workspace rule for this route.
- If Route A/B permits plan content in the WRK body, confirm the gate logic does not accidentally fail those WRKs. If this verifier is only for Route C/file-backed plans, state that explicitly in code and test it.

**Tweak non-HTML gates:**
| Gate | Change | Notes |
|------|-------|-------|
| Integrated test gate | `3-5` → `3+` | Count unique integrated-test refs only; no upper bound |
| Agent log gate | Make optional for single-agent runs | Do not infer “single-agent” from raw log count alone unless that is how the current schema encodes it |
| Stage evidence gate | Keep accepting `stage_evidence_ref` | Add malformed/missing-type handling if absent today |
| Resource-intelligence gate | Accept `"complete"` and `"done"` | Normalize case/whitespace before comparison |
| Future-work gate | Accept simple strings in `recommendations` | Continue accepting object entries too |

Agent-log refinement:
- Skip only when multi-agent execution is not evidenced anywhere.
- If `agent_logs` is present, validate shape and contents even for a single entry.
- If multi-agent metadata exists but logs are missing, still fail.

Future-work refinement:
- Accept both:
  - string entries
  - object entries with `disposition`
- Reject malformed entries like numbers, empty dicts, or blank strings with a clear error.

Resource-intelligence refinement:
- Normalize status values case-insensitively.
- Preserve failure for unknown statuses after normalization.

**Add new gate:**
- `check_github_issue_gate()`
- Validate `github_issue_ref` locally without network or `gh` dependency.
- Accept canonical GitHub issue URLs with optional trailing slash/query string.
- Reject:
  - PR URLs
  - issue comment URLs
  - non-GitHub URLs
  - malformed issue numbers
- Error message should say this is a required replacement for the retired HTML gate.

### 2. `scripts/work-queue/audit-session-signal-coverage.py`

- Remove HTML-only entries from `REQUIRED_SIGNALS`.
- Remove HTML-only inference branches from `_session_infers_signal()`.
- Keep the script tolerant of historical session data if it may still parse older records; it should stop requiring HTML, not crash on seeing it.

### 3. `scripts/work-queue/build-session-gate-analysis.py`

- Remove HTML-only signal definitions and gate keys from current analysis output.
- Keep historical input parsing tolerant if archived data may still contain retired gate names.

### 4. `scripts/work-queue/backfill-categories.py`

- Remove the HTML category regex only if this script is meant to stop classifying historical HTML-era records too.
- If the script still scans old archives, prefer making HTML classification non-required/non-emitted for new records rather than breaking historical backfills unintentionally.

### 5. `scripts/work-queue/gate_checks_archive.py`

- Replace `html_verification_ref` with `github_issue_ref` in `_REQUIRED_FIELDS`.
- Replace file-path validation with local GitHub issue URL validation.
- Decide explicitly whether archived pre-WRK-5104 items are now expected to fail.
  - If yes, document that this is an intentional archive-breaking migration.
  - If no, add a cutover rule or migration path for historical archives.

This is the highest integration risk outside the main verifier because it is itself a hard gate.

### 6. `scripts/work-queue/process.md` (already done)

- `3-5` → `3+` already updated.
- During verification, confirm script behavior matches doc wording so the repo does not drift again.

## Implementation Order

1. **Add/adjust tests first**
   - Add targeted tests for retired HTML gates, new GitHub issue validation, `3+` integrated tests, agent-log optionality, status normalization, and mixed recommendation shapes.
2. **`verify-gate-evidence.py`**
   - Remove HTML-only checks and registrations by gate key/name.
   - Add `check_github_issue_gate()`.
   - Update plan, integrated-test, agent-log, resource-intelligence, and future-work logic.
3. **`gate_checks_archive.py`**
   - Swap archive-required field and validation semantics.
   - Decide and encode historical archive behavior explicitly.
4. **`audit-session-signal-coverage.py`**
   - Remove HTML requirements.
5. **`build-session-gate-analysis.py`**
   - Remove HTML reporting keys.
6. **`backfill-categories.py`**
   - Remove or demote HTML classification only after confirming historical-data intent.
7. **End-to-end verification**
   - Re-run close/stage-14 flow on a GitHub-issue-based WRK.

## Test Plan

| Test | Type | Expected |
|------|------|----------|
| Verifier on WRK-5104 GitHub-issue workflow assets | Happy path | Passes without any HTML artifacts |
| WRK with valid `github_issue_ref` and no HTML fields | Happy path | Passes |
| WRK missing `github_issue_ref` | Error path | Fails with clear replacement message |
| WRK with malformed `github_issue_ref` (`issues/foo`) | Error path | Fails |
| WRK with PR URL instead of issue URL | Error path | Fails |
| WRK with issue comment URL instead of issue URL | Error path | Fails |
| Integrated test count = 2 unique refs | Edge | Fails |
| Integrated test count = 3 unique refs | Edge | Passes |
| Integrated test count = 10 unique refs | Edge | Passes |
| Integrated test list with duplicates totaling 3 but only 2 unique refs | Edge | Fails |
| Future-work with simple string recommendations | Edge | Passes |
| Future-work with mixed string + object recommendations | Edge | Passes |
| Future-work with malformed recommendation entry (`null`, number, empty string) | Edge | Fails clearly |
| Resource-intelligence `completion_status: done` | Edge | Passes |
| Resource-intelligence `completion_status: COMPLETE` | Edge | Passes if normalized |
| Resource-intelligence unknown status | Error path | Fails |
| Single-agent WRK with no agent logs | Edge | Passes if no multi-agent evidence exists |
| Multi-agent WRK missing agent logs | Edge | Fails |
| `spec_ref` present and valid | Happy path | Plan gate passes |
| `spec_ref` missing where required by route | Error path | Plan gate fails clearly |
| `gate_checks_archive.py` with valid `github_issue_ref` URL | Happy path | Passes |
| `gate_checks_archive.py` against historical HTML-era record | Regression/decision test | Behavior matches explicit migration decision |
| Stage 14 pre-exit hook end-to-end | Integration | Full pipeline passes |
| Diagnostic scripts on historical data containing retired HTML signals | Integration | No crash; expected output reflects retired gates |

## Verification

```bash
# Targeted verifier run
uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-5104 --phase close

# Archive gate validation
uv run --no-project python scripts/work-queue/gate_checks_archive.py

# Stage 14 integration
bash scripts/work-queue/exit_stage.py WRK-5104 14

# Regression tests
uv run --no-project python -m pytest scripts/work-queue/tests -v

# If there is a dedicated test file for these gates, run it first for faster feedback
uv run --no-project python -m pytest scripts/work-queue/tests -k "gate_evidence or gate_checks_archive" -v
```

## Codex Notes

- The draft assumes `spec_ref` always replaces `plan_html_review_final_ref`, but that may be wrong if Route A/B plans can live in the WRK body instead of a file. That needs an explicit rule before implementation.
- `check_github_issue_gate()` should not depend on `gh`, network access, or live GitHub resolution. URL-shape validation is the robust option here.
- “Make agent log optional: skip if single-agent (check log count)” is underspecified and risky. Optionality should be driven by workflow evidence, not just how many logs happen to exist.
- The integrated-test change needs uniqueness semantics; otherwise duplicate refs can satisfy `3+` incorrectly.
- The archive-script change is an AC gap in the original draft. If older archived WRKs still use HTML-era fields, this plan must explicitly choose between breaking them or supporting a cutover rule.
- The diagnostic-script removals are called “low risk,” but they can still break nightly cron/reporting if historical data contains retired signals. Keep parsing tolerant even if requirements are removed.
- The draft’s verification commands used bare `python`; they should be `uv run --no-project python ...` throughout, including pytest invocations.
- I could not inspect the live source in this session because shell execution in the workspace is currently failing under sandbox startup, so the refinement above is based on the draft plus workspace policy constraints rather than direct code confirmation.
