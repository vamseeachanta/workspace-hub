# Plan for #2684: env-aware guard — codex emits UNAVAILABLE when running under Claude-Code Bash

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-05-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2684
> **Review artifacts:** scripts/review/results/2026-05-13-plan-2684-claude-r3.md (single-author r3 fallback; T2 fanout still partially-blocked until this plan lands)

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/review/lib/codex-version-guard.sh:24` — `codex_version_guard_check()` is the existing integration point. Returns 0/2/3 with an explanation line on stdout. Already used by `scripts/review/plan-review-fanout.sh:163`.
- Found: `scripts/review/plan-review-fanout.sh:160-169` — codex case branch sources `codex-version-guard.sh`, calls `codex_version_guard_check`, and routes `rc=3` to `write_unavailable` (via `normalize_provider_output`).
- Found: `scripts/review/tests/test_plan_review_fanout.sh:476` — `test_fanout_codex_unavailable_on_bad_version` already covers the version-guard's `INCOMPATIBLE` path via `PLAN_REVIEW_CODEX_VERSION` env injection. New env-aware test should follow this pattern.
- Found: `CLAUDECODE=1` is exported in Claude-Code Bash subprocesses (verified 2026-05-13: `env | grep CLAUDE` returns `CLAUDECODE=1`, `CLAUDE_CODE_SESSION_ID=...`, `CLAUDE_CODE_ENTRYPOINT=cli`, `CLAUDE_CODE_EXECPATH=...`).

### Standards

Not applicable — harness-tooling change.

### LLM Wiki pages consulted

No relevant wiki pages.

### Documents consulted

- Related issue [#2684](https://github.com/vamseeachanta/workspace-hub/issues/2684) — Codex stdin-hang in Claude-Code Bash; root cause documented; 3 candidate fixes; Option 1 (env-aware guard) chosen by user 2026-05-13.
- Related issue [#2683](https://github.com/vamseeachanta/workspace-hub/issues/2683) — sibling Claude-leg fanout fix; just landed at commit `b61f2c5a3` with mechanism deviation from approved plan (lesson: smoke-test the fix in target environment before declaring done).
- Related issue [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) — original 0.124.0 stdin-hang (closed); the version-guard pattern that this plan extends.
- Related issue [#2661](https://github.com/vamseeachanta/workspace-hub/issues/2661) — 0.130.0 ceiling-raise (closed); validation methodology blind spot that let #2684 ship.
- Memory `feedback_codex_cli_0_124_upstream_regression` — historical record section is authoritative on the Claude-Code-Bash stdin layer behavior.

### Gaps identified

1. `codex_version_guard_check` only checks codex VERSION; it has no knowledge of the *invocation environment*. A correct-version codex (0.130.0) running under Claude-Code Bash still hangs — the version check returns `OK` and the fanout invokes codex anyway, hitting the rc=124 hang for 5–10 min (`timeout` default), wasting wall-clock on every fanout run.
2. No structural reason exists for the guard to be version-only; environment-class checks fit the same `0/2/3` return contract.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-13):
- `#2684` — OPEN — `bug(harness): codex-cli 0.130.0 reproduces #2479 stdin-hang...`
- `#2683` — OPEN — `bug(harness): Claude SessionEnd hook...` (about to be closed once wave-2 confirms)
- `#2675` — OPEN — parent plan; needs wave-2 re-dispatch after this plan lands

**File existence** (verified 2026-05-13):
- EXISTS: `scripts/review/lib/codex-version-guard.sh`
- EXISTS: `scripts/review/plan-review-fanout.sh`
- EXISTS: `scripts/review/tests/test_plan_review_fanout.sh`

**Env-var presence** (verified 2026-05-13 via `env | grep -E '^CLAUDE'`):
```
CLAUDECODE=1
CLAUDE_CODE_SESSION_ID=763a24b1-0770-4800-9fd2-54a3870564f7
CLAUDE_CODE_ENTRYPOINT=cli
CLAUDE_CODE_EXECPATH=/home/vamsee/.npm-global/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe
```

Of these, `CLAUDECODE=1` is the canonical boolean flag; the others are value-carriers. Plan uses `CLAUDECODE`.

**Line excerpts** (`sed -n '24,30p' scripts/review/lib/codex-version-guard.sh`):
```
codex_version_guard_check() {
  local bin="${CODEX_BIN:-codex}"
  if ! command -v "$bin" >/dev/null 2>&1 && [[ ! -x "$bin" ]]; then
    echo "codex CLI not on PATH"
    return 2
  fi
  local raw ver base prerelease floor ceiling
```

**Reproduction proofs**: N/A — this is preventive, not failure-reproducing. The failure mode (#2684's codex rc=124) is already documented in the parent issue; this plan adds an upstream guard to *avoid* the failure-mode invocation.

**Source count**: 7 (issue body + 4 related issues + codex-version-guard.sh source + memory rule). Exceeds 3-source minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-13-issue-2684-codex-claudecode-env-guard.md` |
| Implementation | `scripts/review/lib/codex-version-guard.sh` (env check added at the top of `codex_version_guard_check`) |
| Test | `scripts/review/tests/test_plan_review_fanout.sh` (new test asserting UNAVAILABLE under `CLAUDECODE=1`) |
| Plan review — Claude (r3) | `scripts/review/results/2026-05-13-plan-2684-claude-r3.md` |
| Docs index | `docs/plans/README.md` |

---

## Deliverable

`codex_version_guard_check()` (in `scripts/review/lib/codex-version-guard.sh`) returns `rc=3` with an `INCOMPATIBLE` message **before** the version check when `CLAUDECODE=1` is set in the environment. The message names the issue (`#2684`), states the upstream root cause (`openai/codex#19945`), and tells the operator how to recover (dispatch fanout from a plain terminal). Fanout then routes `rc=3` to `write_unavailable` per the existing flow — no fanout changes needed.

---

## Pseudocode

T1 — trivial. See "Files to Change" below.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/review/lib/codex-version-guard.sh` (top of `codex_version_guard_check`, after the `command -v` check) | Add env-aware check for `CLAUDECODE=1`; return 3 with reason before version probing |
| Modify | `scripts/review/tests/test_plan_review_fanout.sh` | Add `test_fanout_codex_unavailable_under_claudecode_env` that sets `CLAUDECODE=1` and asserts the codex artifact contains `INCOMPATIBLE` + `#2684` |
| Update | `docs/plans/README.md` | Add this plan to index |

Exact change in `codex-version-guard.sh`, inserted between the `command -v "$bin"` check (line ~26-30) and the `--version` invocation (line ~32):

```diff
 codex_version_guard_check() {
   local bin="${CODEX_BIN:-codex}"
   if ! command -v "$bin" >/dev/null 2>&1 && [[ ! -x "$bin" ]]; then
     echo "codex CLI not on PATH"
     return 2
   fi
+
+  # Environment guard (#2684): codex exec hangs from Claude-Code Bash regardless
+  # of codex version. The Claude-Code Bash tool provides a non-closeable stdin
+  # layer that does not propagate EOF to the codex subprocess (upstream
+  # openai/codex#19945). Detect via CLAUDECODE=1 (set by Claude Code in every
+  # Bash subprocess) and fail fast with a clear reason so the operator can
+  # dispatch from a plain terminal for Codex review.
+  if [[ "${CLAUDECODE:-}" == "1" ]]; then
+    echo "INCOMPATIBLE (running under Claude-Code Bash — codex exec stdin-hangs regardless of version; upstream openai/codex#19945; see workspace-hub #2684; dispatch fanout from a plain terminal for Codex review)"
+    return 3
+  fi
 
   local raw ver base prerelease floor ceiling
```

New test in `test_plan_review_fanout.sh`, modeled on `test_fanout_codex_unavailable_on_bad_version` (which already exists and uses the same env-injection harness):

```bash
test_fanout_codex_unavailable_under_claudecode_env() {
  run_test "codex env-guard emits UNAVAILABLE when CLAUDECODE=1 (#2684)"

  local td; td="$(mktemp -d)"
  CLAUDECODE=1 run_wrapper_under_mocks "$td" >/dev/null 2>&1 || true

  local codex_art cap
  codex_art="$(ls "$td/results/"*-plan-9999-codex.md 2>/dev/null | head -1)"
  cap="$td/captures/codex.capture"
  if [[ -z "$codex_art" ]]; then
    fail "codex artifact missing after CLAUDECODE=1 env guard"
  elif ! grep -qF 'UNAVAILABLE' "$codex_art"; then
    fail "CLAUDECODE=1 did not produce UNAVAILABLE artifact" "$(head -20 "$codex_art")"
  elif ! grep -qF '#2684' "$codex_art"; then
    fail "UNAVAILABLE artifact missing #2684 reference" "$(head -20 "$codex_art")"
  elif [[ -f "$cap" ]] && grep -qF 'ARGV: exec' "$cap"; then
    fail "codex exec was invoked despite CLAUDECODE env guard" "$(head -5 "$cap")"
  else
    pass "CLAUDECODE=1 guard wrote UNAVAILABLE and skipped codex exec"
  fi
  rm -rf "$td"
}
```

And add the test to the runner list near the existing `test_fanout_codex_unavailable_on_bad_version`.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_fanout_codex_unavailable_under_claudecode_env` | When `CLAUDECODE=1`, the codex leg writes UNAVAILABLE referencing `#2684` and does NOT invoke `codex exec` | `CLAUDECODE=1` set in wrapper invocation env | codex artifact contains `UNAVAILABLE` + `#2684`; no `ARGV: exec` in capture |
| Existing `test_fanout_codex_unavailable_on_bad_version` | Unchanged | `PLAN_REVIEW_CODEX_VERSION="codex-cli 0.128.0"` | (still passes — env check fires only when CLAUDECODE=1) |
| Smoke (manual, post-implementation) | `CLAUDECODE=1 bash scripts/review/plan-review-fanout.sh <a-plan-file>` produces a codex artifact with INCOMPATIBLE + #2684, completes in <10s (not stuck for `PLAN_REVIEW_PROVIDER_TIMEOUT_SEC=600`) | live invocation | codex artifact + immediate completion |

---

## Acceptance Criteria

- [ ] `grep -c 'CLAUDECODE' scripts/review/lib/codex-version-guard.sh` returns ≥1
- [ ] `grep -c '#2684' scripts/review/lib/codex-version-guard.sh` returns ≥1
- [ ] Fanout test suite goes 19 → 20 with all tests green
- [ ] Live re-run of `bash scripts/review/plan-review-fanout.sh <plan-file>` from this Claude-Code session produces a codex artifact with `INCOMPATIBLE` and `#2684`, and completes the codex leg in <10s (not stuck at provider timeout)
- [ ] When the same command is run from a non-Claude-Code terminal (CLAUDECODE unset), the env check skips and the existing version check runs normally
- [ ] Plan registered in `docs/plans/README.md`
- [ ] No regression in other 18 fanout tests

---

## Adversarial Review Summary

Single-author r3 fallback per `feedback_permission_gate_blocks_cross_review`. T2 fanout is technically usable for Claude+Gemini *now* (post-#2683), but #2684 itself is in the codex path it would test — and the env guard this plan adds would emit UNAVAILABLE for codex anyway. So T1 single-provider review depth is correct here, not degraded.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (main session, r3) | MINOR | 4 findings: 1 MAJOR-but-non-blocking (false-positive risk under unexpected `CLAUDECODE` exports — operator-facing override hint missing from INCOMPATIBLE message), 3 MINOR (test-mechanism subtlety not commented; process-tree DiD revisit-trigger unnamed; INCOMPATIBLE message length cosmetic). 10 affirmative checks all pass: ≥3 sources, env-var verified, diff mechanically correct, fail-fast ordering preserved, test pattern matches existing, return-code contract preserved, CLAUDECODE vs SESSION_ID selection correct, complexity T1 defensible, acceptance criteria falsifiable, risks identify the right concerns. |

**Overall result:** **MINOR — can advance to `status:plan-review` for user approval.** All 4 findings are additive refinements; none change design. Review artifact at `scripts/review/results/2026-05-13-plan-2684-claude-r3.md`.

If approved as-is, finding #1 (operator-facing override hint in INCOMPATIBLE message) is worth folding in during execution; findings 2–4 are cosmetic and can skip.

---

## Risks and Open Questions

- **Risk:** `CLAUDECODE` is an Anthropic-controlled env-var name; a future Claude Code release could rename or remove it. If renamed, the env guard silently stops firing and the fanout regresses to the old "wait for `timeout`" path. Mitigation: the regression test runs in CI; if a future Claude Code release removes `CLAUDECODE` from Bash subprocesses, the test still passes (mock CLI invocation works), but live fanout breaks. Possible defense: also check `CLAUDE_CODE_SESSION_ID` as fallback, or any `CLAUDE_CODE_*` prefix match. Defer to follow-up if a rename ever happens.
- **Risk:** false positives — `CLAUDECODE=1` might be set in environments where codex actually works (e.g., a future fix from openai/codex). The guard would then incorrectly block codex. Mitigation: env-var unset is a one-line override (`CLAUDECODE= bash plan-review-fanout.sh ...`) and the issue body documents this; document it in the guard's INCOMPATIBLE message too.
- **Open:** Should the env-guard also check process-tree for `claude` ancestor as defense-in-depth? Subagent's analysis suggested env-var-only is sufficient; process-tree adds complexity (different `ps` formats across OS) and is brittle. Decision: env-var only for v1; revisit if env-var proves insufficient.
- **Open:** Should #2684 be **closed** once this plan lands, or kept open with a "deferred upstream fix" status? Decision: close once landed; track the upstream fix (Option 3 in the issue body) as a follow-up issue if/when re-opening `openai/codex#19945` is pursued.

---

## Complexity: T1

**T1** — ~8-line addition to an existing function in a single file + 1 new test in an existing test file + 1 docs/plans index row. No new files. No design decisions beyond "use `CLAUDECODE=1` as the detection signal" (already determined by user direction + env-var inspection). Patch is mechanically clear; behavioral test is straightforward.
