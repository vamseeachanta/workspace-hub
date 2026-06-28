# Plan for #3294: Make adversarial-review dispatchers run headless (codex `env -u CLAUDECODE`, gemini non-interactive)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3294
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3294-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

This is a harness/infrastructure issue scoped entirely to `scripts/review/` shell dispatchers. No wiki content, no engineering standards, no client data — `Client: N/A`.

### Existing repo code

- **Found:** `scripts/review/plan-review-fanout.sh` — the parallel fan-out wrapper. The codex leg lives at lines 163–183 and the gemini leg at lines 184–192. The codex leg sources `lib/codex-version-guard.sh` (line 174), runs `codex_version_guard_check` in the **current** shell (line 176), and on `guard_rc==3` writes an `UNAVAILABLE` stub (lines 177–179) without ever invoking codex. The exec path (line 181) already uses `timeout … codex exec "$combined" … </dev/null`.
- **Found:** `scripts/review/lib/codex-version-guard.sh` lines 37–40 — an **environment guard** that short-circuits: `if [[ "${CLAUDECODE:-}" == "1" ]]; then echo "INCOMPATIBLE (…)"; return 3; fi`. This fires **before** the version-band check (lines 42–79). Net effect: under Claude-Code Bash (`CLAUDECODE=1`), the guard returns 3 regardless of codex version, so the fanout codex leg always degrades to `UNAVAILABLE`.
- **Found:** gemini leg `scripts/review/plan-review-fanout.sh:190-191` — `( cd /tmp && GEMINI_CLI_TRUST_WORKSPACE=… timeout -k 5s "${timeout_s}s" gemini -p "$combined" ) > "$out" 2>"$err" || rc=$?`. **Confirmed: there is no `</dev/null`** on this invocation. An interactive `Opening authentication page in your browser. Do you want to continue? [Y/n]:` prompt therefore reads the inherited (non-tty, non-EOF) stdin and blocks until the 600 s `timeout` kills it — the "hang until killed" the issue reports.
- **Found:** `scripts/review/submit-to-codex.sh` lines 99–111 — the standalone codex dispatcher (called by `cross-review.sh`) runs the same guard and `exit 7` on `guard_rc==3`; its codex exec path (`run_codex_exec`, lines 214–232) already closes stdin with `</dev/null` but does **not** strip `CLAUDECODE`, so it also fast-fails under Claude-Code Bash.
- **Found:** `scripts/review/submit-to-gemini.sh` lines 188–216 (`run_gemini_once`) pipes `INPUT_TEXT` into `gemini -p … --yolo --output-format json` via `printf '%s\n' "$INPUT_TEXT" | … gemini …`. **Re-verified 2026-06-28:** because the prompt is delivered through a pipe, gemini's stdin is the `printf` output, which reaches EOF immediately after the text. So `submit-to-gemini.sh` does **not** share the fanout leg's inherited-open-stdin hang vector — an interactive `[Y/n]` would consume the piped text then hit EOF and abort, not block to timeout. `--yolo` auto-approves *tool* calls, not *auth*. The auth-prompt risk here is therefore materially lower than in the fanout leg, and any change here is polish rather than the load-bearing fix (see Scope below).
- **Gap:** no code path strips `CLAUDECODE` before invoking codex in any dispatcher; the **fanout** gemini leg does not close stdin and can block to timeout on an interactive prompt.

### Standards

Not applicable — infrastructure/shell issue, no engineering standard involved.

### LLM Wiki pages consulted

No relevant wiki pages — dispatcher plumbing, not domain knowledge.

### Documents consulted

- Issue **#3294** body (source) — names the three target scripts and the two failure modes (codex `rc=3`/stdin-hang under `CLAUDECODE`; gemini interactive-auth hang). Parent epic **#3290**, Theme B (review-gate reliability).
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` Step 3 — the review step whose prose must be updated per acceptance criterion 3 ("Documented in … the issue-planning-mode review step").
- `scripts/review/tests/test_plan_review_fanout.sh` — existing harness. `run_wrapper_under_mocks` (lines 21–40) **unsets `CLAUDECODE` by default** (line 37) precisely so the #2684 env-guard doesn't block tests; this is the seam a new test re-sets `CLAUDECODE=1` through to prove the strip works. **Critical:** `test_fanout_codex_unavailable_under_claudecode_env` (lines 522–547) currently asserts the *opposite* of this plan's target behavior — it requires that under `CLAUDECODE=1` the codex artifact is `UNAVAILABLE` **and** that `ARGV: exec` does **not** appear in the capture. This plan **inverts** that test (see TDD Test List, MAJOR-1 below). `test_codex_invocation_inlines_plan_body` (160–184), `test_gemini_invocation_inlines_plan_body` (186–208), and `test_fanout_codex_unavailable_on_bad_version` (549–570) are the patterns to extend.
- `scripts/review/tests/test_codex_version_guard.sh` — the guard's own unit tests. **Re-verified 2026-06-28: this file has NO test for the `CLAUDECODE==1 → return 3` branch** (grep finds zero `CLAUDECODE` references). That branch's only live coverage is the fanout test this plan inverts — so the inversion creates a coverage hole unless a guard-level unit test is added (see MAJOR-2 below).
- `scripts/review/tests/mocks/{codex,gemini}` — capture argv + PWD + env + stdin to `$PLAN_REVIEW_CAPTURE_DIR`. The gemini mock already echoes `GEMINI_CLI_TRUST_WORKSPACE`; **neither mock currently echoes `CLAUDECODE`** — that line must be added to assert the strip.
- Referenced upstream/prior issues: `openai/codex#19945` (stdin-hang), workspace-hub **#2684** (env-guard origin), **#2479** (version-band guard), **#1326** (gemini capacity fallback).

### Cross-cutting epic decisions (owner-confirmed 2026-06-28) — applicability to #3294

The 2026-06-28 owner decisions D1–D6 govern **sibling** issues under epic #3290 (D1 schema → #3295/#3282; D2 CI caching → #3291; D3 determinism → #3282/#3283; D4 discovery → #3284; D5 governance → #3296; D6 sequencing defers #3283 to Wave 2). **None of them touch #3294's surface**, which is the three `scripts/review/` shell dispatchers and their tests — no envelope schema, no CI workflow caching, no determinism fields, no discovery registry, no auto-apply governance. Recorded here explicitly so reviewers see they were considered and found out-of-scope; #3294 carries no open question that overlaps D1–D6.

### Gaps identified

- No mechanism strips `CLAUDECODE` for the codex subprocess in `plan-review-fanout.sh` or `submit-to-codex.sh`.
- The **fanout** gemini leg does not close stdin → hangs to timeout on interactive auth. (`submit-to-gemini.sh` is pipe-fed and does not share this vector.)
- Test mocks do not record `CLAUDECODE`, so no regression can currently assert it is stripped.
- An existing test (`test_fanout_codex_unavailable_under_claudecode_env`) hard-asserts the pre-fix behavior and **will fail after the fix** unless explicitly inverted.
- The guard's kept `CLAUDECODE→return 3` safety-net branch has no unit-level coverage once the fanout test is inverted.

### Evidence (embedded verification)

**Issue status** (verified 2026-06-28 via `gh issue view`):
- `#3294` — OPEN — "seamless(review): make adversarial-review dispatchers run headless (codex env -u CLAUDECODE, gemini non-interactive)"

**Live environment probe** (2026-06-28):
```
CLAUDECODE=[1]
codex:  /home/vamsee/.npm-global/bin/codex   -> @openai/codex 0.142.3
gemini: /home/vamsee/.npm-global/bin/gemini  -> @google/gemini-cli 0.49.0
GEMINI_API_KEY: (unset)   GOOGLE_API_KEY: (unset)
~/.codex/auth.json        EXISTS (codex authenticated)
~/.gemini/oauth_creds.json EXISTS (gemini OAuth cached, mtime 2026-06-22)
```

**File existence** (`ls` 2026-06-28):
- EXISTS: scripts/review/plan-review-fanout.sh
- EXISTS: scripts/review/lib/codex-version-guard.sh
- EXISTS: scripts/review/submit-to-codex.sh
- EXISTS: scripts/review/submit-to-gemini.sh
- EXISTS: scripts/review/tests/test_plan_review_fanout.sh
- EXISTS: scripts/review/tests/test_codex_version_guard.sh
- EXISTS: scripts/review/tests/mocks/codex, scripts/review/tests/mocks/gemini
- THIS PLAN: docs/plans/2026-06-28-issue-3294-review-dispatcher-headless.md (revised in place this round)

**Line excerpts** (the defects + the contradicted test):
```
# lib/codex-version-guard.sh:37-40  (codex fast-fails to UNAVAILABLE under CLAUDECODE)
  if [[ "${CLAUDECODE:-}" == "1" ]]; then
    echo "INCOMPATIBLE (running under Claude-Code Bash — codex exec stdin-hangs…#2684…)"
    return 3
  fi

# plan-review-fanout.sh:190-191  (gemini leg: NO </dev/null -> interactive auth hangs to timeout)
      ( cd /tmp && GEMINI_CLI_TRUST_WORKSPACE="${GEMINI_CLI_TRUST_WORKSPACE:-true}" \
          timeout -k 5s "${timeout_s}s" gemini -p "$combined" ) > "$out" 2>"$err" || rc=$?

# test_plan_review_fanout.sh:541-542  (THE CONTRADICTED TEST — asserts codex must NOT run under CLAUDECODE)
  elif [[ -f "$cap" ]] && grep -qF 'ARGV: exec' "$cap"; then
    fail "codex exec was invoked despite CLAUDECODE env guard" "$(head -5 "$cap")"
```

**Version-band proof** — installed codex `0.142.3` is `>=` the guard ceiling `CODEX_VERSION_GUARD_CEILING_DEFAULT=0.130.0` (`lib/codex-version-guard.sh:11`), so once `CLAUDECODE` is stripped the guard returns `OK (…past whitelisted regression band)` (lib lines 69–72) and codex exec runs normally. Under the mocks (`mock codex --version` = `codex-cli 0.123.0`, below the `0.124.0` floor → `OK (… pre-regression)`), the strip likewise yields a real codex run. The **only** thing forcing `UNAVAILABLE` today is the `CLAUDECODE==1` short-circuit.

**Reproduction proofs** (verify-against-repo-state, per Step 1.5):

The issue alleges runtime behavior (codex degrades to UNAVAILABLE; gemini hangs). A *live* CLI reproduction is **blocked by the analysis sandbox**: every Bash command that sources `codex-version-guard.sh` or otherwise references `codex`/runs the guard is denied. The failure is instead established **deterministically from code + a verified environment probe**, sound because both failure modes are unconditional given the observed state:

1. `CLAUDECODE=1` is confirmed live in this exact Bash environment (probe above).
2. `lib/codex-version-guard.sh:37-40` returns `3` whenever `CLAUDECODE==1`, *before* any version check — a static, branch-unconditional fact. `plan-review-fanout.sh:177-179` converts `guard_rc==3` into an `UNAVAILABLE` stub. ⇒ codex leg is UNAVAILABLE in-environment, every run.
3. `plan-review-fanout.sh:190-191` omits `</dev/null`; an interactive `[Y/n]` auth prompt on inherited non-tty stdin blocks until `timeout` (default 600 s) kills it. ⇒ gemini leg hangs.

- Reproduced at: 2026-06-28 (static trace + live env probe; live CLI run sandbox-denied — documented honestly, not skipped).
- Failure mode observed matches issue claim: YES for both legs (codex→UNAVAILABLE, gemini→hang-to-timeout). The codex symptom in-repo is the *degraded UNAVAILABLE* (guard already intercepts the raw stdin-hang); the fix must make it actually **run**, not just fail cleanly.

<!-- Distinct sources: issue #3294, plan-review-fanout.sh, codex-version-guard.sh, submit-to-codex.sh, submit-to-gemini.sh, test_plan_review_fanout.sh, test_codex_version_guard.sh, mocks, issue-planning-mode SKILL = 9 (>=3 required). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3294-review-dispatcher-headless.md |
| Tests (fanout) | `scripts/review/tests/test_plan_review_fanout.sh` |
| Tests (guard unit) | `scripts/review/tests/test_codex_version_guard.sh` |
| Test mocks | `scripts/review/tests/mocks/codex`, `scripts/review/tests/mocks/gemini` |
| Implementation (primary) | `scripts/review/plan-review-fanout.sh` |
| Implementation (secondary) | `scripts/review/submit-to-codex.sh`, `scripts/review/submit-to-gemini.sh` |
| Plan review — Claude | scripts/review/results/2026-06-28-plan-3294-claude.md |
| Plan review — Codex | scripts/review/results/2026-06-28-plan-3294-codex.md |
| Plan review — Gemini | scripts/review/results/2026-06-28-plan-3294-gemini.md |
| Docs updates | issue-planning-mode SKILL.md Step 3 note; dispatcher header comments |

---

## Deliverable

A `plan-review-fanout.sh` (plus `submit-to-codex.sh` and an optional `submit-to-gemini.sh` polish) that, when run from a Claude-Code Bash session, produces a **genuine Codex review** by stripping `CLAUDECODE` for the codex subprocess, and a **genuine-or-fast-`UNAVAILABLE` Gemini result** by closing the fanout leg's stdin — with every leg hard-bounded so the fanout never hangs and never silently degrades to one provider. The existing test that hard-codes the pre-fix codex behavior is **inverted**, and the guard's retained `CLAUDECODE` safety-net branch gains a dedicated unit test.

---

## Scope (honest boundary)

- **Load-bearing fixes (required for acceptance):**
  1. Codex fanout leg: run the version guard **and** `codex exec` with `CLAUDECODE` stripped, so codex actually runs while the version-band guard still governs.
  2. Gemini fanout leg: append `</dev/null` so an interactive prompt gets EOF and the leg fails fast instead of blocking to timeout. **This stdin closure is the primary remedy** — not the auth pre-check.
  3. `submit-to-codex.sh`: `unset CLAUDECODE` so its guard + `run_codex_exec` run headless.
  4. Invert `test_fanout_codex_unavailable_under_claudecode_env` and add the guard-unit test (below) so the suite encodes the new contract and keeps the retained branch covered.
- **Secondary / defense-in-depth (NOT the acceptance gate):**
  - A `gemini_auth_present()` fast-path in the fanout leg is **optional polish**. The plan's own evidence (Risks below) shows cached creds existed yet gemini still prompted on 2026-06-27, so an auth pre-check cannot be the primary fix — `</dev/null` is. The pre-check only shortens the already-bounded wait when auth is *obviously* absent.
  - `submit-to-gemini.sh` is pipe-fed and does **not** share the hang vector; an auth pre-check there is optional polish, lower priority, and explicitly not required for acceptance.

---

## Pseudocode

```
# --- codex leg (plan-review-fanout.sh) ---
codex)
  combined = PROMPT + "--- PLAN ---" + body
  source lib/codex-version-guard.sh
  # #3294: run the guard with CLAUDECODE stripped (subshell scope) so its
  # env-branch (lib:37-40) does not fire; the version-band check then governs
  # (mock 0.123.0 => OK pre-regression; live 0.142.3 => OK past ceiling).
  guard_msg = $( unset CLAUDECODE; codex_version_guard_check ) ; guard_rc=$?
  if guard_rc == 3:
      write_unavailable(codex, 3, guard_msg)        # genuine version incompatibility only
  else:
      # strip CLAUDECODE for the codex subprocess (openai/codex#19945, #2684);
      # keep existing </dev/null + timeout.
      env -u CLAUDECODE timeout -k 5s ${timeout_s}s codex exec "$combined" \
          > out 2> err </dev/null  || rc=$?

# --- gemini leg (plan-review-fanout.sh) ---
gemini)
  combined = PROMPT + "--- PLAN ---" + body
  # OPTIONAL fast-path (defense-in-depth, NOT the primary fix):
  if NOT gemini_auth_present():          # GEMINI_API_KEY|GOOGLE_API_KEY|~/.gemini/oauth_creds.json
      write_unavailable(gemini, 0, "no non-interactive gemini auth configured")
  else:
      # PRIMARY FIX: close stdin so an interactive [Y/n] auth prompt gets EOF and
      # aborts in seconds instead of blocking to timeout; keep cwd=/tmp + trust env.
      ( cd /tmp && GEMINI_CLI_TRUST_WORKSPACE=true \
          timeout -k 5s ${timeout_s}s gemini -p "$combined" \
          </dev/null > out 2> err ) || rc=$?

gemini_auth_present():           # test-overridable via GEMINI_NO_AUTH / GEMINI_AUTH_PROBE
  [[ -n GEMINI_API_KEY || -n GOOGLE_API_KEY || -f ${GEMINI_HOME:-~/.gemini}/oauth_creds.json ]]
```

`submit-to-codex.sh`: add `unset CLAUDECODE` once near the top (Settled Decision SD-1: global). The whole script exists to invoke codex; nothing downstream consumes `CLAUDECODE` (the renderer is a pure `uv run python` child, the attestation script reads files, neither branches on it), so the blast radius of a global unset is the codex subprocess + harmless removal of a marker var from child env. Both the guard (lines 99–111) and `run_codex_exec` then run with it stripped.

`submit-to-gemini.sh`: `</dev/null` is **not applicable** (it pipes `INPUT_TEXT` via stdin, which already supplies EOF). An optional `gemini_auth_present` fast-path mirroring the fanout helper MAY be added before the retry loop as polish; it is not required for acceptance and carries its own small test only if implemented.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/review/plan-review-fanout.sh` | codex leg: run guard + exec with `CLAUDECODE` stripped; gemini leg: `</dev/null` (primary) + optional auth fast-path |
| Modify | `scripts/review/submit-to-codex.sh` | global `unset CLAUDECODE` (SD-1) so guard+exec run headless from Claude-Code Bash |
| Modify (optional) | `scripts/review/submit-to-gemini.sh` | optional auth fast-path polish — NOT required for acceptance (pipe already supplies EOF) |
| Modify | `scripts/review/tests/mocks/codex` | echo `CLAUDECODE: ${CLAUDECODE:-(unset)}` so a test can assert it is stripped |
| Modify | `scripts/review/tests/mocks/gemini` | echo `CLAUDECODE` + ensure STDIN-EOF is observable |
| **Modify (INVERT)** | `scripts/review/tests/test_plan_review_fanout.sh` | **replace** `test_fanout_codex_unavailable_under_claudecode_env` with the inverted/new tests below; update the runner list (remove the old name at line ~588, add the new names) |
| Modify | `scripts/review/tests/test_codex_version_guard.sh` | add a guard-unit test pinning the retained `CLAUDECODE→return 3` safety-net branch (MAJOR-2) |
| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | Step 3 note: fanout is headless by default (acceptance criterion 3) |
| Update | `docs/plans/README.md` | add this plan's index row |

---

## TDD Test List

> **MAJOR-1 (the contradicted test).** `test_fanout_codex_unavailable_under_claudecode_env` (test_plan_review_fanout.sh:522–547) asserts the *pre-fix* contract: under `CLAUDECODE=1`, codex artifact = `UNAVAILABLE`, `#2684` referenced, and `ARGV: exec` absent. After this fix, codex **does** run under `CLAUDECODE=1`, so that test would fail. It is **inverted/replaced** by `test_codex_leg_strips_claudecode` + `test_codex_produces_review_under_claudecode`, and removed from the runner list. The plan's AC "all fanout tests pass" is only honest with this inversion done.

> **MAJOR-2 (coverage of the retained branch).** Inverting MAJOR-1's test removes the only live coverage of the guard's deliberate `CLAUDECODE→return 3` branch (which this plan KEEPS for un-migrated direct callers). `test_codex_version_guard.sh` has none today (verified). Add `test_guard_returns_3_under_claudecode` there so a future cleanup can't silently delete the safety net.

| Test name | File | What it verifies | Expected input | Expected output |
|---|---|---|---|---|
| `test_codex_leg_strips_claudecode` | fanout | codex subprocess sees `CLAUDECODE` unset even when wrapper runs with `CLAUDECODE=1` | run wrapper, `extra_env=(CLAUDECODE=1)` | `codex.capture` shows `CLAUDECODE: (unset)` (not `1`) |
| `test_codex_produces_review_under_claudecode` *(inverts the old test)* | fanout | under `CLAUDECODE=1` the codex artifact is a real review AND `codex exec` actually ran | wrapper, `CLAUDECODE=1`, mock codex 0.123.x | `…-codex.md` contains `## Verdict` + `Mock finding from codex`, NOT `UNAVAILABLE`; `codex.capture` contains `ARGV: exec` |
| `test_codex_guard_still_blocks_genuine_bad_version` | fanout | stripping `CLAUDECODE` does not defeat the version-band guard | `PLAN_REVIEW_CODEX_VERSION="codex-cli 0.128.0"`, `CLAUDECODE=1` | `…-codex.md` = `UNAVAILABLE` + `INCOMPATIBLE`; `codex.capture` has no `ARGV: exec` |
| `test_guard_returns_3_under_claudecode` | guard unit | retained safety-net branch still returns 3 + #2684 msg for direct callers that do NOT strip | `CLAUDECODE=1 codex_version_guard_check` (called directly) | rc==3, output contains `#2684` and `INCOMPATIBLE` |
| `test_gemini_leg_closes_stdin` | fanout | gemini leg gets EOF on stdin (no interactive hang) — **the primary fix** | wrapper run | `gemini.capture` STDIN section empty/EOF |
| `test_gemini_unavailable_when_no_auth` *(secondary path)* | fanout | when the optional fast-path is enabled, missing auth → fast `UNAVAILABLE`, no `gemini` invocation | `GEMINI_NO_AUTH=1` | `…-gemini.md` = `UNAVAILABLE (… no … auth …)`; `gemini.capture` absent |
| `test_gemini_does_not_block_other_legs` | fanout | a hanging/auth-prompt gemini does not stall codex/claude | mock gemini that reads stdin then exits | all three artifacts present; wrapper exits within timeout |
| `test_fanout_no_provider_hangs_under_claudecode` | fanout | end-to-end: `CLAUDECODE=1` run yields 3 non-empty artifacts, no hang | wrapper, `CLAUDECODE=1` | 3 artifacts; ≤ a few seconds with mocks |

Runner-list edit: delete the `test_fanout_codex_unavailable_under_claudecode_env` invocation (line ~588) and add the new fanout test names; add `test_guard_returns_3_under_claudecode` to the guard-unit runner.

Test seam for the optional gemini fast-path: add an optional `GEMINI_NO_AUTH`/`GEMINI_AUTH_PROBE` override (mirroring `GEMINI_CMD` in `submit-to-gemini.sh`) so tests force the no-auth branch without depending on the real `~/.gemini`. If the fast-path is descoped to a later iteration, `test_gemini_unavailable_when_no_auth` ships with it (not before).

---

## Acceptance Criteria

- [ ] From a Claude-Code Bash session, `plan-review-fanout.sh <plan>` produces a **non-empty Codex review** (not an `UNAVAILABLE` stub) and a **non-empty Gemini review or a clean `UNAVAILABLE`** — with no manual step and no hang.
- [ ] Regression test asserts the codex invocation runs with `CLAUDECODE` stripped AND that codex actually executes (`test_codex_leg_strips_claudecode` + `test_codex_produces_review_under_claudecode`).
- [ ] The pre-fix test `test_fanout_codex_unavailable_under_claudecode_env` is **inverted/removed**, and the runner list no longer references it — the suite encodes the new "codex runs under CLAUDECODE" contract.
- [ ] The retained guard `CLAUDECODE→return 3` branch keeps unit coverage via `test_guard_returns_3_under_claudecode` in `test_codex_version_guard.sh`.
- [ ] The version-band guard still rejects genuinely-bad codex versions after the strip (`test_codex_guard_still_blocks_genuine_bad_version`).
- [ ] Gemini fanout leg closes stdin (`</dev/null`) — the primary, AC-gating fix; no leg can stall the fanout past its per-provider timeout.
- [ ] All fanout tests pass: `bash scripts/review/tests/test_plan_review_fanout.sh` (consistent with the inverted test).
- [ ] Codex/version-guard tests still pass and now include the new branch test: `bash scripts/review/tests/test_codex_version_guard.sh`.
- [ ] Documented in the dispatcher header comments (plan-review-fanout.sh, submit-to-codex.sh) and the issue-planning-mode Step 3 note.
- [ ] Review artifacts posted to `scripts/review/results/`.

---

## Adversarial Review Summary

<!-- Round-2 dispatched review pending. Do not post to GitHub until populated. -->

| Round | Date | Providers | Verdict | Notes |
|---|---|---|---|---|
| Round-1 | 2026-06-28 | Claude + Codex (Gemini best-effort) | **MAJOR** | 4 findings: (1) contradicted test `test_fanout_codex_unavailable_under_claudecode_env` would fail post-fix yet AC claimed all-pass; (2) inverting it strips the only coverage of the retained guard branch; (3) gemini auth pre-check framed as the fix but contradicted by the plan's own "creds present yet still prompted" evidence; (4) `submit-to-gemini.sh` claimed to share the hang vector but is pipe-fed (already EOF). |
| Round-2 | (pending) | Claude + Codex (Gemini best-effort) | **PENDING** | Re-review of this revision. |

Revisions made in response to Round-1:
- Inverted `test_fanout_codex_unavailable_under_claudecode_env` → `test_codex_produces_review_under_claudecode` (+ explicit runner-list edit + Files-to-Change row marked INVERT). AC now requires the inversion.
- Added MAJOR-2 guard-unit test `test_guard_returns_3_under_claudecode` in `test_codex_version_guard.sh` to keep the retained branch covered.
- Reframed gemini fix: `</dev/null` stdin closure is the **load-bearing, AC-gating** fix; the auth pre-check is demoted to optional defense-in-depth. New "Scope (honest boundary)" section makes this explicit.
- Corrected the `submit-to-gemini.sh` analysis: it is pipe-fed (EOF already supplied), does not share the hang vector; its change is optional polish, not required for acceptance.
- Recorded that cross-cutting decisions D1–D6 belong to sibling issues and do not affect #3294's scope; settled the two prior open questions (SD-1, SD-2 below).

---

## Settled Decisions

- **SD-1 — `submit-to-codex.sh` strip scope:** use a **global** `unset CLAUDECODE` near the top (one-line comment referencing #3294/#2684), not a per-function scope. Rationale: the whole script exists to invoke codex; no downstream child branches on `CLAUDECODE`; global is the simplest defensible choice and matches the script's single responsibility. (Resolves Round-1 open question.)
- **SD-2 — symmetry of the strip:** **do NOT** strip `CLAUDECODE` for the claude or gemini legs. Scope the strip to the codex paths only, to minimize blast radius. `claude -p` and `gemini -p` do not exhibit the codex stdin-EOF defect. (Resolves Round-1 open question.)

---

## Risks and Open Questions

- **Risk (review bootstrap / chicken-and-egg):** the plan review for #3294 must itself run through the very dispatchers being fixed. Until the fix lands, run the review with the documented workaround `env -u CLAUDECODE bash scripts/review/plan-review-fanout.sh …` (codex) and accept a fast `UNAVAILABLE` gemini leg if auth prompts. Document this in the review artifacts.
- **Risk (guard intent — retained branch):** the `CLAUDECODE==1` branch in `lib/codex-version-guard.sh` is a *deliberate* safety net for callers that do not strip the env. This plan does **not** remove it — it strips `CLAUDECODE` *before* calling the guard so the branch simply doesn't fire for migrated callers, and adds `test_guard_returns_3_under_claudecode` so the branch stays covered after the fanout test is inverted.
- **Risk (gemini auth still prompts despite cached creds):** `~/.gemini/oauth_creds.json` existed yet the 2026-06-27 run still prompted (likely token-refresh). This is precisely why the auth pre-check is **not** the primary fix — the **`</dev/null` stdin closure is load-bearing** (converts a 600 s hang into a seconds-fast `UNAVAILABLE`). The auth pre-check is optional defense-in-depth.
- **Risk (per-provider timeout default 600 s):** even with the fixes, a degraded leg waits up to `PLAN_REVIEW_PROVIDER_TIMEOUT_SEC`. A shorter dedicated gemini auth-probe timeout is flagged as optional, not required for acceptance.
- **Open:** whether to ship the optional gemini auth fast-path (`gemini_auth_present` + `test_gemini_unavailable_when_no_auth`) in this iteration or defer it. Recommend shipping the fast-path in the fanout leg (cheap, well-tested) but treating it as non-gating; defer the `submit-to-gemini.sh` polish unless reviewer asks for it. Flag for reviewer.

---

## Complexity: T2

**T2** — multi-file shell-harness change (2 required dispatchers + 1 optional + 2 test files + 2 mocks + 1 doc + README) with mandatory TDD, mechanically bounded (env strip + stdin close; no algorithm), but touching the review gate itself and **inverting an existing regression test** — which raises the review bar. Kept at T2 with explicit two-provider review (Claude + Codex; Gemini best-effort) and a documented review-bootstrap workaround for the chicken-and-egg risk.
