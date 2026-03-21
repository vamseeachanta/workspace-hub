YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
YOLO mode is enabled. All tool calls will be automatically approved.
# WRK-5107: Purge HTML Gates from verify-gate-evidence.py (Refined Plan)

## Context

WRK-5104 replaced the HTML lifecycle with GitHub issues. `verify-gate-evidence.py` still enforces HTML-era artifact checks, blocking stage 14 for all WRKs using the new workflow. User decision: **replace entirely** (no backward compat). 

*Reliability Stance:* Removing backward compatibility introduces risks for scripts that iterate over historical WRKs. We must ensure that the removal of these gates fails safely for missing fields, and that new gates (like GitHub issue validation) do not introduce flaky network dependencies or break downstream metric pipelines.

## Files to Modify

### 1. `scripts/work-queue/verify-gate-evidence.py` (primary — ~1960 lines)

**Remove these HTML-era functions:**
| Function | Replacement / Reliability Note |
|----------|--------------------------------|
| `check_browser_open_elapsed_time()` | Remove entirely. Ensure any callers are safely purged. |
| `check_html_open_default_browser_gate()` | Replace with `check_github_issue_gate()`. **Do not perform HTTP GET requests to validate the URL** (avoids rate-limiting/flaky gates). Use strict regex validation (e.g., `^https://(?:www\.)?github\.com/[^/]+/[^/]+/issues/\d+$`). |
| `check_user_review_publish_gate()` | Remove entirely. |
| `check_plan_confirmation()` | Replace: accept `spec_ref` → plan.md instead of `plan_html_review_final_ref`. Use `.get('spec_ref')` safely to handle missing keys without `KeyError`. |
| `check_plan_publish_predates_approval()` | Remove entirely. |

**Remove from gate registry:**
- Purge `html_open_required` list and its usage.
- Purge HTML gates from the registration block.

**Tweak non-HTML gates:**
| Gate | Change / Reliability Note |
|------|---------------------------|
| Integrated test | `3-5` → `3+`. Ensure type safety (cast to `int` inside a `try/except` block to prevent crashes on malformed frontmatter). |
| Agent log | Make optional: skip if single-agent. Determine "single-agent" robustly (e.g., check if log array length <= 1, handling `None` gracefully). |
| Stage evidence | Accept `stage_evidence_ref` (already does). Ensure file path resolution handles edge cases (e.g., path traversal attempts). |
| Resource-intelligence | Add `"complete"` and `"done"` to valid `completion_status` values. Use case-insensitive matching. |
| Future-work | Accept simple strings in `recommendations` list. Check that `isinstance(item, str)` or `isinstance(item, dict)` to prevent iteration crashes on `None`. |

### 2. `scripts/work-queue/audit-session-signal-coverage.py`
- Remove HTML signal entries from `REQUIRED_SIGNALS` and HTML branches in `_session_infers_signal()`.
- *Risk:* If this script runs on historical sessions, removing these might cause validation errors on old data. Ensure the script defaults safely if it encounters legacy HTML signals in old data.

### 3. `scripts/work-queue/build-session-gate-analysis.py`
- Remove HTML signal definitions and gate keys.
- *Risk:* Downstream dashboards parsing the analysis output might break if keys suddenly disappear. Ensure the schema output remains valid.

### 4. `scripts/work-queue/backfill-categories.py`
- Remove HTML category regex pattern.
- *Risk:* Ensure removing this regex doesn't cause uncaught exceptions when processing legacy descriptions that contain HTML-specific verbiage.

### 5. `scripts/work-queue/gate_checks_archive.py`
- Replace `html_verification_ref` with `github_issue_ref` in `_REQUIRED_FIELDS`.
- Update validation to check URL format. Use the same robust regex defined in `verify-gate-evidence.py` to ensure consistency.

## Implementation Order

1. **gate_checks_archive.py** — swap `html_verification_ref` → `github_issue_ref` (Establish the new baseline schema).
2. **verify-gate-evidence.py** — remove HTML functions, add `check_github_issue_gate()`, tweak 5 gates.
3. **audit-session-signal-coverage.py** — remove HTML signals.
4. **build-session-gate-analysis.py** — remove HTML signals.
5. **backfill-categories.py** — remove HTML regex.

## Test Plan

| Test | Type | Expected |
|------|------|----------|
| Run `verify-gate-evidence.py` against WRK-5104 assets | Happy path | All gates pass |
| Run against a WRK with `github_issue_ref` but no HTML artifacts | Happy path | Pass |
| Run against a WRK missing `github_issue_ref` | Error path | Fail with clear gate failure message (no stack trace) |
| Run with malformed `github_issue_ref` (e.g., local path or invalid URL) | Error path | Fail with regex validation error |
| Integrated test count = `abc` (malformed) | Edge | Fail gracefully (no crash) |
| Future-work with empty list or missing key | Edge | Pass or fail gracefully depending on exact requirement |
| `gate_checks_archive.py` with valid `github_issue_ref` URL | Happy path | Archive gate passes |
| Verify no HTTP/network calls are made during execution | Reliability | Zero network egress |

## Verification

```bash
# Unit: run verifier against WRK-5104
python scripts/work-queue/verify-gate-evidence.py WRK-5104 --phase close

# Integration: stage 14 exit hook
bash scripts/work-queue/exit_stage.py WRK-5104 14

# Regression: run existing tests
python -m pytest scripts/work-queue/tests/ -v
```

---

## Gemini Notes

*The prompt contained 5 specific review requests. While they reference components outside the direct scope of the WRK-5107 draft (e.g., `portfolio-signals.yaml`, L3 output parsing), here is my systems reliability assessment applied to those concepts within the context of gate verification and automated workflows:*

1. **Failure modes in L3 gemini output parsing:** 
   If gate checks or upstream agents rely on parsing LLM output (L3), assuming clean YAML or JSON is a critical failure mode. The output might contain markdown fences (````yaml...````), conversational prose ("Here is the plan..."), or truncated data. 
   *Mitigation:* Use robust regex extractors to strip out fences before passing to `yaml.safe_load`. Wrap all parsing in `try/except` blocks that trigger an explicit "Agent Output Malformed" gate failure rather than a python stack trace.

2. **Carry-forward logic (`portfolio-signals.yaml`):** 
   If any gate relies on state files like `portfolio-signals.yaml`, file I/O operations must be defensive. 
   *Mitigation:* If the file is missing, empty, or corrupt, the script must not crash. It should log a warning, fall back to a safe default (e.g., `{}`), or trigger a specific gate failure (`STATE_FILE_CORRUPT`). Never trust the file system state implicitly in an automated pipeline.

3. **Challenge the dual-mode tie-break (`engineering >= harness`):** 
   Hardcoding a strict `>` or `>=` threshold in dual-mode tie-breaks is brittle. If false positives spike, a code change is required to adjust it.
   *Mitigation:* Ensure this threshold is pulled from a configuration file or environment variable (e.g., `TIE_BREAK_THRESHOLD`). Furthermore, analyze if a flat `>=` is appropriate—sometimes a weighted heuristic is more stable against edge cases.

4. **Review test coverage (Are 16 tests sufficient?):** 
   For a surface area that involves regex validation, type coercion (int casting), and multiple missing-key permutations across 6 different gates, 16 tests are likely insufficient.
   *Mitigation:* Implement parameterized testing (`@pytest.mark.parametrize`) to quickly scale test coverage across boundary conditions (e.g., test counts at 0, 2, 3, 5, 10, malformed strings, nulls) without writing dozens of individual test functions.

5. **Identify nightly cron risks:** 
   - *3am quota:* If network calls were used for GitHub validation, a cron job processing 100+ WRKs would quickly hit API quotas and fail randomly. (This is why regex validation is enforced in the refined plan).
   - *Version drift:* Explicitly pin dependencies (e.g., in `uv.lock` or `requirements.txt`) so cron environments don't accidentally run with a newer, incompatible version of a YAML parser or the Gemini CLI.
   - *File lock races:* If the cron job archives or modifies WRK states concurrently, ensure atomic file writes or implement `.lock` files to prevent corrupted frontmatter during parallel executions.
