# Plan for #3896: agy lane silently drops plans above ~30 KB on Windows (argv limit)

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-10-07
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3896
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-10-07-plan-3896-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `scripts/review/submit-to-agy.sh` (121 lines) — comment at line 12 states "agy ignores stdin → content rides the --print value (argv), so it is ARG_MAX-bounded"; line 64 sets `AGY_MAX_BYTES="${AGY_MAX_BYTES:-1000000}"` (1 MB default, sized for Linux ARG_MAX ~2 MB); the `AGY_REVIEW_MODE=1` oversize guard at lines 70–74 exits 3 only when `_content_bytes > AGY_MAX_BYTES` — a 28 KB plan (28,000 bytes) is under 1,000,000, so this guard never fires on Windows despite Windows CreateProcess limit of ~32,767 chars.
- EXISTS: `scripts/review/plan-review-fanout.sh` — lines 105–134 `normalize_provider_output` function: when rc=0 AND stdout empty (lines 125–131), writes `UNAVAILABLE (agy CLI failed, rc=0: empty provider output)`. This is the path that launders the Windows platform-cap failure into a legitimate-looking T3→T2 degradation.
- EXISTS: `scripts/review/validate-review-output.sh` and `scripts/review/normalize-verdicts.sh` — both have `INVALID_OUTPUT` handling paths (confirmed by grep); `INVALID_OUTPUT` is a hard gate in cross-review.sh (line 444–448 for agy lane), while `UNAVAILABLE` is a graceful degradation. The two statuses carry different downstream consequences.
- EXISTS: `scripts/review/results/2026-09-03-plan-3816-agy.md` and `scripts/review/results/2026-10-05-3943-agy-unavailable.md` — review result artifacts demonstrating the existing output format.

### Standards

Not applicable — this is a review-infrastructure shell script issue.

### LLM Wiki pages consulted

No relevant wiki pages — agy dispatch is a local tooling concern.

### Documents consulted

- Issue body [#3896](https://github.com/vamseeachanta/workspace-hub/issues/3896) — provides controlled-pair evidence: 20,525 B → rc=0 normal output; 41,000 B → rc=126 `# agy dispatch failed`. Identifies three defects: wrong platform cap, UNAVAILABLE vs INVALID_OUTPUT misclassification, and unconfirmed exit-status propagation through fanout.
- `scripts/review/cross-review.sh` lines 419–448 — confirms `INVALID_OUTPUT` is a hard gate for the agy lane (blocks rather than degrades); `UNAVAILABLE` is a soft degradation. The distinction is load-bearing for review routing.
- `scripts/review/submit-to-agy.sh:61–74` — existing `AGY_REVIEW_MODE=1` guard correctly exits 3 for oversized payloads, but the threshold (1 MB) is wrong for Windows. The emit at line 71 prints to stdout as a comment string (`# agy review failed: ...`) which `normalize_provider_output` would classify as non-empty output and validate; however, the `AGY_REVIEW_MODE` string does not include `## Verdict` / `## Findings` / `## Blockers` sections, so `validate-review-output.sh` would return `INVALID_OUTPUT`. This path works correctly; the Windows defect is that this path is never reached because 28 KB < 1 MB.

### Gaps identified

- No platform-detection logic exists in `submit-to-agy.sh` or anywhere in `scripts/review/`.
- No `AGY_MAX_BYTES_WINDOWS` variable or equivalent per-platform cap constant.
- No regression test for the Windows argv-limit failure path (test fixtures in `scripts/review/tests/` do not cover payload-size guards on the Windows cap).

### Evidence (embedded verification)

**Issue status** (verified 2026-10-07 via `gh issue view`):
- `#3896` — OPEN — bug(review): agy lane silently drops plans above ~30 KB on Windows (argv limit), recorded as provider outage

**File existence** (`ls` 2026-10-07 from live clone):
- EXISTS: `scripts/review/submit-to-agy.sh`
- EXISTS: `scripts/review/plan-review-fanout.sh`
- EXISTS: `scripts/review/validate-review-output.sh`
- EXISTS: `scripts/review/normalize-verdicts.sh`
- EXISTS: `scripts/review/cross-review.sh`
- MISSING (new — this plan creates): no new files; modifications to `submit-to-agy.sh` only

**Line excerpts** (from live checkout):
```
submit-to-agy.sh:12-13:
#   * agy ignores stdin -> content rides the --print value (argv), so it is ARG_MAX-
#     bounded; we cap it (AGY_MAX_BYTES, default 1 MB, well under ~2 MB ARG_MAX).

submit-to-agy.sh:64:
AGY_MAX_BYTES="${AGY_MAX_BYTES:-1000000}"

submit-to-agy.sh:70-73:
if [[ "${AGY_REVIEW_MODE:-0}" == "1" && "$_content_bytes" -gt "$AGY_MAX_BYTES" ]]; then
  echo "# agy review failed: payload exceeds review cap (${_content_bytes} > ${AGY_MAX_BYTES} bytes; AGY_REVIEW_MODE=1 forbids truncation)"
  echo "# agy review failed: payload exceeds review cap — chunk the content or use a lane without the argv bound" >&2
  exit 3
fi

plan-review-fanout.sh:125-131:
  if [[ ! -s "$out" ]]; then
    local reason
    reason="empty provider output"
    if [[ -s "$err" ]]; then
      reason="$(error_excerpt "$err")"
    fi
    write_unavailable "$prov" "0" "$reason" "$out"
  fi
```

**Reproduction proofs:**
- Controlled pair from issue body: 20,525 B plan → rc=0, normal output (587 chars); 41,000 B plan → rc=126, `# agy dispatch failed (rc=126)` — reproduced by issue author 2026-09-25 on Windows host.
- The rc=0 / empty-output observation from fanout: explained by the Windows case where `agy` accepts the truncated argv and returns rc=0 with no output (not yet empirically reproduced through fanout — issue marks this as "not established").
- Reproduced at: 2026-09-25 (issue author); code path confirmed by source read 2026-10-07.
- Failure mode observed matches issue claim: YES — the cap threshold mismatch is confirmed by source read; the rc=0 propagation path requires Windows-side empirical reproduction.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-10-07-issue-3896-agy-argv-windows-cap.md` |
| Implementation | `scripts/review/submit-to-agy.sh` |
| Tests | `scripts/review/tests/test_submit_to_agy.sh` (new or extend) |
| Plan review — Claude | `scripts/review/results/2026-10-07-plan-3896-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-10-07-plan-3896-codex.md` |
| Plan review — Agy | `scripts/review/results/2026-10-07-plan-3896-agy.md` |

---

## Deliverable

`submit-to-agy.sh` detects the Windows platform and applies a platform-aware content cap (~25,000 chars) before dispatch; when `AGY_REVIEW_MODE=1` and the platform cap is exceeded, the script exits 3 and emits a structured `# agy review failed` comment (existing pattern) so downstream validators classify it as `INVALID_OUTPUT` rather than `UNAVAILABLE`.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/review/submit-to-agy.sh` | Add platform detection + per-platform cap constant + correct REVIEW_MODE guard threshold |
| Create/extend | `scripts/review/tests/test_submit_to_agy.sh` | Add regression test for >30KB payload in AGY_REVIEW_MODE on simulated Windows cap |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_review_mode_exits3_at_windows_cap` | AGY_REVIEW_MODE=1 + payload >25 KB exits 3 when `AGY_PLATFORM=windows` is set | 30,000-byte fixture file + `AGY_REVIEW_MODE=1 AGY_PLATFORM=windows` | exit 3, stdout contains `# agy review failed:` |
| `test_review_mode_passes_under_windows_cap` | AGY_REVIEW_MODE=1 + payload <25 KB proceeds normally on windows cap | 20,000-byte fixture + `AGY_REVIEW_MODE=1 AGY_PLATFORM=windows` + `AGY_CMD=<mock>` | exit 0, mock called with combined payload |
| `test_review_mode_allows_large_payload_on_linux` | 1 MB cap still applies on Linux; 100 KB payload is allowed | 100,000-byte fixture + `AGY_REVIEW_MODE=1 AGY_PLATFORM=linux` + `AGY_CMD=<mock>` | exit 0, mock called |
| `test_review_mode_exits3_at_linux_cap` | Linux 1 MB cap still enforced | 1,100,000-byte fixture + `AGY_REVIEW_MODE=1 AGY_PLATFORM=linux` | exit 3 |
| `test_truncation_still_works_outside_review_mode` | non-review truncation path unchanged | 30,000-byte fixture + `AGY_PLATFORM=windows` (no REVIEW_MODE) | exit same as mock, content truncated to cap |

---

## Acceptance Criteria

- [ ] All new tests pass: `bash scripts/review/tests/test_submit_to_agy.sh`
- [ ] On a simulated Windows cap (`AGY_PLATFORM=windows AGY_MAX_BYTES_WINDOWS=25000 AGY_REVIEW_MODE=1`), a 30 KB plan file causes exit 3 with a `# agy review failed:` line on stdout
- [ ] `normalize_provider_output` in `plan-review-fanout.sh` receives the rc=3 exit and produces an `UNAVAILABLE` stub (existing behavior for rc≠0) — no change to fanout needed; the fix is in submit-to-agy.sh emitting a non-zero rc
- [ ] `validate-review-output.sh` classifies the rc=3 stub as `INVALID_OUTPUT` (confirmed by existing logic that checks for `## Verdict` / `## Findings` / `## Blockers` sections, which the stub does not contain)
- [ ] `AGY_MAX_BYTES` override still works: setting `AGY_MAX_BYTES=500` with `AGY_REVIEW_MODE=1` and a 1 KB file exits 3
- [ ] No regression: existing tests in `scripts/review/tests/` pass

---

## Adversarial Review Summary

*To be filled after Step 4 completes.*

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | — |
| Codex | — | — |
| Agy | — | — |

---

## Risks and Open Questions

- **Risk:** Platform detection via `$OSTYPE` or `uname` in Git Bash on Windows returns `msys` or `cygwin` — implementer must verify the detection string empirically on the target Windows host before relying on it.
- **Risk:** The rc=0 / empty-stdout path (where `agy` itself exits 0 with no output on Windows) is described in the issue as unconfirmed. The fix (exit 3 before dispatch when cap exceeded) prevents the path from being reached; if the cap detection fires correctly, the rc=0 case becomes unreachable. If the cap detection fails (e.g., platform detection wrong), the rc=0 / empty case remains. Tests must cover both the guard-fires path and mock the mock-passes path.
- **Open:** Should `AGY_MAX_BYTES_WINDOWS` be a separate variable or computed from a single `AGY_PLATFORM_MAX_CHARS` variable? The current `AGY_MAX_BYTES` already governs truncation for the non-review path; a separate Windows-specific variable avoids breaking the existing truncation cap. Recommend: separate `AGY_MAX_BYTES_WINDOWS` defaulting to 25000.

---

## Complexity: T1

Single script file modified (`submit-to-agy.sh`) plus one test file extended. No new modules, no schema changes, no cross-repo edits. Platform detection is a one-liner (`[[ "$(uname -s)" == MINGW* || "$(uname -s)" == CYGWIN* ]]`). All downstream infrastructure (fanout, validate, normalize) requires no change.
