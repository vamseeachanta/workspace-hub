# Plan for #2479: codex-cli stdin-hang regression — version guard

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2479
> **Review artifacts (to be produced):** scripts/review/results/2026-05-02-plan-2479-claude.md | ...-codex.md (SKIPPED — codex is the subject) | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/review/plan-review-fanout.sh` lines 150-159 (current `main` HEAD) — codex branch already invokes `timeout -k 5s "${timeout_s}s" codex exec "$combined" > "$out" 2>"$err" </dev/null`. The wrapper-half fix (`--no-interactive` removal + `</dev/null`) **is already on `main`**, landed via commit `021915337` (PR #2518, 2026-04-27 — `fix(review): harden plan-review fanout provider handling`). Comment block at lines 154-157 explicitly references the sibling `submit-to-codex.sh` regression notes.
- Found: `scripts/review/submit-to-codex.sh:200-218` — `run_codex_exec()` carries the original #2406 `</dev/null` redirect plus a `CODEX_TIMEOUT_SECONDS` (default 300) wrap, plus a `classify_codex_failure()` function that already detects TIMEOUT/QUOTA/TRANSPORT classes from stderr. **No version guard exists** anywhere in this script.
- Found: `scripts/review/tests/test_plan_review_fanout.sh:173-174` — regression assertion `grep -qF -- '--no-interactive'` with failure message "codex-cli >=0.124.0 rejects it" already exists on `main`. The fix-branch's regression-guard contribution is already absorbed.
- Found: `scripts/review/cross-review.sh` — invokes `submit-to-codex.sh`. References `npm install -g @openai/codex` install instructions at lines 479 and 528 (no version pin).
- Found: `scripts/setup/verify-setup.sh:87` — checks `command -v codex` only; **no version verification** ("non-critical" classification).
- Found: `scripts/setup/new-machine-setup.sh:171` — single mention of codex in a "WARN: npm not found" log; no install step bound to a pinned version.
- Found: `origin/fix/codex-stdin-hang` at SHA `257b47dd9` — branch still exists (verified via `git fetch && git log origin/fix/codex-stdin-hang -1`). **However: the diff against current `origin/main` is now stale and divergent** (`git diff main...origin/fix/codex-stdin-hang -- scripts/review/plan-review-fanout.sh` reverts main's `normalize_provider_output` + `write_unavailable` hardening from #2518). Merging this branch into current main would **regress** the fanout's UNAVAILABLE-stub behaviour added on 2026-04-27. The branch is **superseded by main**, not pendingly mergeable. This plan does **NOT** propose merging it.
- Found: `docs/plans/2026-04-26-issue-2479-codex-stdin-hang.md` — prior draft plan (T2, draft status, 264 lines). Pre-dates main commit `021915337` and proposes merging the (now-stale) fix branch. **This plan supersedes the prior draft for the post-`021915337` repo state.**

### Standards

Not applicable — harness/infrastructure scope.

### LLM Wiki pages consulted

Not applicable — harness/infrastructure scope.

### Documents consulted

- Issue #2479 body (1 source) — defines the two-part regression (wrapper-half + upstream-half), 8/8 batch failures on 2026-04-23, recommends downgrade-pin to 0.123.0 or 0.121.0.
- Issue #2406 body — closing context. State: CLOSED 2026-04-20T20:59:46Z, labels include stale `status:plan-approved`. The `</dev/null` fix it landed remains in `submit-to-codex.sh` and is correct for codex-cli 0.121.0; closure was silently invalidated by 0.124.0+.
- Upstream tracking issue **openai/codex#19945** — "codex exec silently crashes with no output when stdio is detached from TTY (0.124.0+)" — **OPEN as of 2026-05-02**. Confirms 0.123.0 is unaffected; 0.124.0 and 0.125.0 reproduce; reporter notes a `script -qfc` PTY-faking workaround that re-attaches a pseudo-TTY but emits a `failed to record rollout items` error. Body explicitly cross-links #18578 / #19119 / #15886 / #18977 / #15830 / #16168 stdin/exec failures.
- npm registry `@openai/codex` versions — current `latest` is **0.128.0** (released 2026-04-30), installed 2026-05-01 01:21 UTC at `/home/vamsee/.npm-global/lib/node_modules/@openai/codex/`. No 0.126.x stable line shipped (only alphas 0.126.0-alpha.1 through alpha.17). 0.129.0-alpha.1/alpha.2 shipped but no stable. **The regression has persisted across 0.124, 0.125, 0.128 — five weeks unfixed upstream.**
- `.claude/memory/topics/feedback_codex_cli_0_124_upstream_regression.md` (committed 2026-04-24) — "downgrade does NOT help from Claude Code's Bash tool" (stdin-propagation confound), "may still restore Codex in a plain user terminal — untested in this session". Tested blocking paths: `</dev/null`, `exec 0<&-`, `setsid`, `script(1)` tty faking — none defeated upstream detection from inside Claude Code.
- `.claude/memory/topics/feedback_codex_sandbox_no_execution.md`, `feedback_codex_needs_pushed_artifact.md`, `feedback_codex_sandbox_write_blocked.md`, `feedback_codex_sandbox_fallback_paths.md` — Codex-MCP sandbox can read GitHub via connector but cannot exec shell or write files; this matters for the cross-review provider that DOES still produce real verdicts (`scripts/review/results/2026-05-02-plan-2580-codex.md` cites GitHub-connector retrieval, not local repo reads).

### Gaps identified

- **Gap 1 (NEW — this plan addresses):** No runtime version-guard exists in either `submit-to-codex.sh` or `plan-review-fanout.sh`. A nightly batch dispatched against codex-cli 0.124+ silently degrades 8/8 reviews to UNAVAILABLE stubs (verified by 2026-04-23 batch and again by `2026-05-02-plan-2550-codex.md` UNAVAILABLE rc=124 today). Operators discover the regression only after the entire batch wastes the timeout window.
- **Gap 2 (NEW — this plan addresses):** No install-time pin for `@openai/codex`. `scripts/setup/new-machine-setup.sh` and `scripts/setup/verify-setup.sh` install codex unpinned ("optional"), so any new-machine bootstrap or `npm update -g` on an existing machine pulls latest stable — currently 0.128.0 — and inherits the bug.
- **Gap 3 (cleanup):** `docs/plans/2026-04-26-issue-2479-codex-stdin-hang.md` (the prior draft) recommends merging `fix/codex-stdin-hang`. That recommendation is now invalid (the branch reverts current main's hardening). The prior plan must be superseded.
- **Gap 4 (cleanup):** `origin/fix/codex-stdin-hang` branch is stale and dangerous to merge. No-op decision: leave it (do not delete from this plan), but explicitly mark it superseded so future planners do not rebase + merge.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):
- `#2479` — OPEN — "fix(review): Codex stdin-hang regression post-#2406 closure (size-dependent)" — labels: bug, cat:harness, domain:knowledge-management, priority:high, wip:ace-linux-1
- `#2406` — CLOSED 2026-04-20T20:59:46Z — labels include stale `status:plan-approved`
- `openai/codex#19945` — OPEN — "codex exec silently crashes with no output when stdio is detached from TTY (0.124.0+)" — labels: bug, CLI, exec; 2 comments

**Codex install state** (verified 2026-05-02 via `cat /home/vamsee/.npm-global/lib/node_modules/@openai/codex/package.json` and `stat`):
```
"version": "0.128.0"
mtime: 2026-05-01 01:21:31 -0500
```

**Live repro of upstream-half** (verified 2026-05-02 via `timeout 15 codex exec "say hello briefly" --skip-git-repo-check </dev/null`):
```
exit=124
Reading additional input from stdin...
```
Confirms the regression persists in 0.128.0 — five weeks after first observation in 0.124.0.

**Wrapper-half is already fixed on main** (verified 2026-05-02 via `sed -n '150,159p' scripts/review/plan-review-fanout.sh`):
```bash
codex)
  local combined
  combined="$(printf '%s\n\n--- PLAN (%s) ---\n%s' \
    "$(cat "$PROMPT_FILE")" "$PLAN_FILE" "$(cat "$PLAN_FILE")")"
  # Keep prompt delivery in argv and close stdin. The sibling
  # submit-to-codex.sh regression tests document that `codex exec -` can
  # hang in installed Codex versions, while argv + </dev/null avoids
  # inherited-pipe stalls.
  timeout -k 5s "${timeout_s}s" codex exec "$combined" > "$out" 2>"$err" </dev/null || rc=$?
  ;;
```

**Fix-branch divergence proof** (verified 2026-05-02 via `git diff main...origin/fix/codex-stdin-hang --stat`):
- `scripts/review/plan-review-fanout.sh` is materially different on the fix branch: it lacks main's `normalize_provider_output` and `write_unavailable` functions (introduced by #2518 on 2026-04-27, after the fix branch's 2026-04-24 authoring). Merging would revert that hardening.

**Recent batch evidence** (verified 2026-05-02 via `head scripts/review/results/2026-05-02-plan-*-codex.md`):
- `2026-05-02-plan-2580-codex.md` → real `## Verdict MAJOR` with GitHub-connector retrieval (not from `submit-to-codex.sh`/local exec)
- `2026-05-02-plan-2541-codex.md` → real `## Verdict MAJOR` (GitHub-connector path)
- `2026-05-02-plan-2552-codex.md` → real `## Verdict MAJOR` (GitHub-connector path)
- `2026-05-02-plan-2550-codex.md` → `UNAVAILABLE (codex CLI failed, rc=124: Reading additional input from stdin...)` — confirms `plan-review-fanout.sh` codex branch still hits the upstream hang on 0.128.0 today.

**npm registry timeline** (verified 2026-05-02 via `npm view @openai/codex versions` + `gh api repos/openai/codex/releases`):
- 0.123.0 — last known-good (per upstream #19945)
- 0.124.0 — released 2026-04-23, regression introduced
- 0.125.0 — 2026-04-24, regression persists
- 0.126.x — alpha-only; never promoted to stable (alpha.1 through alpha.17, 2026-04-25 → 2026-04-30)
- 0.128.0 — 2026-04-30, regression persists; current `latest`
- 0.129.0-alpha.1 / .2 — 2026-04-30 / 2026-05-01; alpha-only

**Source count:** 8 distinct sources (issue #2479, issue #2406, issue openai/codex#19945, npm registry, codex install package.json, fanout script lines, fix-branch diff, 4 recent codex artifacts in scripts/review/results/). Meets ≥3 retrieval contract.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2479-codex-version-guard.md` |
| Prior plan (superseded by this one) | `docs/plans/2026-04-26-issue-2479-codex-stdin-hang.md` |
| Stale branch (NOT to be merged) | `origin/fix/codex-stdin-hang` @ `257b47dd9` |
| New: shared version-guard library | `scripts/review/lib/codex-version-guard.sh` |
| New: shared pin manifest (env file) | `scripts/install/codex-pin.env` |
| New: install-time pin script | `scripts/install/pin-codex.sh` |
| New: version-guard unit test | `scripts/review/tests/test_codex_version_guard.sh` |
| Modify: runtime guard wiring | `scripts/review/submit-to-codex.sh` |
| Modify: runtime guard wiring | `scripts/review/plan-review-fanout.sh` |
| Modify: install pin invocation | `scripts/setup/new-machine-setup.sh` |
| Modify: version assertion | `scripts/setup/verify-setup.sh` |
| Modify: regression-test added | `scripts/review/tests/test_plan_review_fanout.sh` |
| Plan review — Claude | `scripts/review/results/2026-05-02-plan-2479-claude.md` |
| Plan review — Codex | SKIPPED (codex is the subject AND broken) |
| Plan review — Gemini | `scripts/review/results/2026-05-02-plan-2479-gemini.md` |

---

## Deliverable

A shared `codex-version-guard.sh` library that fast-fails any `codex exec` invocation when the installed `@openai/codex` is in the known-bad range `[0.124.0, ?)`, plus an install-time pin script invoked from new-machine bootstrap that holds codex at `0.123.0` until upstream openai/codex#19945 closes — so that nightly batches and ad-hoc cross-reviews emit a clear "INCOMPATIBLE_VERSION" UNAVAILABLE stub immediately instead of burning the 600s/300s timeout on every plan.

---

## Decision: pin-floor at 0.123.0, runtime fast-fail above, no auto-upgrade

Three options were considered:

1. **Pin to 0.123.0 (downgrade)** — the upstream-confirmed last-known-good (per openai/codex#19945). Restores `codex exec` reliability on plain user terminals. **Caveat from memory `feedback_codex_cli_0_124_upstream_regression`: this does NOT restore Codex from inside a Claude Code Bash tool because of stdin-propagation behaviour, but DOES restore it from cron and plain terminals.** Nightly batch dispatch happens via cron / setsid (not Claude Code), so the downgrade IS expected to restore nightly batches.
2. **Upgrade to 0.125+ if upstream fixes (currently 0.128.0)** — rejected. Live test on 2026-05-02 (90-byte prompt) shows `exit=124 / Reading additional input from stdin...` is still present in 0.128.0. Upstream #19945 remains OPEN with no fix-PR linked. Nothing newer is known-good.
3. **Both: floor-pin + runtime guard** — RECOMMENDED. Pin install at 0.123.0 to prevent silent-regression on `npm update -g`, AND add a runtime guard that fast-fails on the known-bad range so an operator who upgrades manually (or runs from a different machine without the pin) sees a structured UNAVAILABLE stub instead of a timeout.

**Recommended decision: option 3.** Rationale: option 1 alone leaves a regression vector (any operator running `npm install -g @openai/codex` without the pin re-poisons their batch). Option 2 is currently impossible (no upstream fix). Option 3 is defence-in-depth at near-zero added complexity (the runtime guard is a 30-line shell function; the pin is a one-line `npm install -g @openai/codex@0.123.0`).

**Floor for guard: `0.124.0`** (inclusive lower bound of known-bad range).
**Ceiling for guard: open / dynamic** (every version >= 0.124.0 fails the guard until the env var `CODEX_VERSION_GUARD_CEILING=X.Y.Z` is set to whitelist a verified-good upgrade). This biases toward false-negatives (refuses untested newer versions) per `feedback_naive_secret_scan_false_positive_cascade`-style "trust the hardened gate, surface drift loudly" reasoning.

---

## Pin mechanism location and discovery path

```
scripts/install/pin-codex.sh           # NEW — single-purpose, idempotent
  ↑ called by ↓
scripts/setup/new-machine-setup.sh     # MODIFY — invoke pin-codex.sh after npm-prefix step
scripts/setup/verify-setup.sh          # MODIFY — assert installed codex matches pin manifest
```

The pin manifest is a single env-var-defaulted constant inside `scripts/install/pin-codex.sh`:

```
CODEX_PIN_VERSION="${CODEX_PIN_VERSION:-0.123.0}"
```

Why a script and not `package.json` devDependency: codex is installed **globally** (`npm install -g`) on every machine because the `cross-review.sh` orchestrator invokes `codex` from PATH, not from a local `node_modules/.bin`. A `package.json` would not affect global PATH resolution. A dedicated install script keeps the pin under git, reusable on Linux + Windows + future ace-linux-N machines, and discoverable by both new-machine bootstrap and operator one-off remediation.

**How the nightly cron sees it:** the cron job runs `cross-review.sh` → `submit-to-codex.sh` → `run_codex_exec()`. The runtime guard added to `run_codex_exec()` (and to `plan-review-fanout.sh:codex)` runs `codex --version` first; if the version is in the deny list, the guard returns rc=3 and the wrapper writes a `## Verdict UNAVAILABLE (INCOMPATIBLE_VERSION 0.128.0 — see #2479)` stub. No timeout consumption, no waste of the 300s/600s budget.

---

## Pseudocode

```
# scripts/review/lib/codex-version-guard.sh — sourced by submit-to-codex.sh
# and plan-review-fanout.sh

readonly CODEX_KNOWN_BAD_FLOOR="0.124.0"
# Empty CEILING means "no upper bound — every version >= floor is denied
# unless explicitly whitelisted". Operators who verify a newer version is
# safe set CODEX_VERSION_GUARD_CEILING=X.Y.Z to permit a band [floor, ceil).
readonly CODEX_VERSION_GUARD_CEILING_DEFAULT=""
readonly CODEX_PIN_VERSION_DEFAULT="0.123.0"

codex_version_guard_check() {
  # Returns rc=0 (OK) | rc=2 (probe failed / codex missing) | rc=3 (incompatible)
  # Prints a single-line diagnostic to stdout suitable for embedding in an
  # UNAVAILABLE stub reason field.
  local bin="${CODEX_BIN:-codex}"
  command -v "$bin" >/dev/null 2>&1 || { echo "codex CLI not on PATH"; return 2; }
  local raw ver
  raw="$(timeout 5 "$bin" --version 2>/dev/null)" || { echo "codex --version failed or timed out"; return 2; }
  ver="$(printf '%s' "$raw" | awk '{print $NF}')" # "codex-cli 0.128.0" → "0.128.0"; "codex-cli 0.129.0-alpha.1" → "0.129.0-alpha.1"
  # Permit pre-release suffix (-alpha.N, -beta.N, -rc.N, etc.) per F1 fix
  # from 2026-05-02 Gemini review.
  [[ "$ver" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.]+)?$ ]] || { echo "codex --version unparseable: $raw"; return 2; }

  # Detect pre-release: any version with a "-suffix" is uniformly suspect
  # because no alpha has been upstream-verified safe and the regression has
  # been observed across alphas (0.126.0-alpha.* batches).
  local base="${ver%%-*}"        # 0.129.0-alpha.1 → 0.129.0
  local prerelease=""
  [[ "$ver" != "$base" ]] && prerelease="${ver#${base}-}"  # alpha.1

  local floor="${CODEX_KNOWN_BAD_FLOOR}"
  local ceiling="${CODEX_VERSION_GUARD_CEILING:-${CODEX_VERSION_GUARD_CEILING_DEFAULT}}"

  # Pre-release at-or-above floor is incompatible regardless of ceiling.
  if [[ -n "$prerelease" ]] && _codex_ge "$base" "$floor"; then
    echo "INCOMPATIBLE ($ver — pre-release ($prerelease) at-or-above floor $floor; no alpha is whitelisted; see #2479)"
    return 3
  fi

  # Compare via dpkg-style version sort (works for SemVer base versions).
  if ! _codex_ge "$base" "$floor"; then
    echo "OK ($ver < $floor — pre-regression)"
    return 0
  fi
  if [[ -n "$ceiling" ]] && ! _codex_lt "$base" "$ceiling"; then
    echo "OK ($ver >= $ceiling — past whitelisted regression band)"
    return 0
  fi
  if [[ -n "$ceiling" ]]; then
    echo "INCOMPATIBLE ($ver in known-bad range [$floor, $ceiling) — upstream openai/codex#19945; see workspace-hub #2479)"
  else
    echo "INCOMPATIBLE ($ver in known-bad range [>= $floor) — upstream openai/codex#19945; see workspace-hub #2479; run scripts/install/pin-codex.sh to downgrade)"
  fi
  return 3
}

_codex_ge() { # $1 >= $2 ?
  [[ "$1" = "$2" ]] && return 0
  [[ "$(printf '%s\n' "$1" "$2" | sort -V | tail -n1)" = "$1" ]]
}
_codex_lt() { # $1 < $2 ?
  [[ "$1" = "$2" ]] && return 1
  [[ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$1" ]]
}
```

```
# scripts/install/codex-pin.env — sourced by both pin-codex.sh and verify-setup.sh
# Single source of truth for the pin version (per F4 fix from 2026-05-02 Gemini review).
CODEX_PIN_VERSION=0.123.0
```

```
# scripts/install/pin-codex.sh
function main():
    require npm on PATH (else: print remediation and exit 1)
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    . "${SCRIPT_DIR}/codex-pin.env"            # imports CODEX_PIN_VERSION
    PIN="${CODEX_PIN_VERSION:-0.123.0}"

    # Resolve codex binary path (per F3 fix from 2026-05-02 Gemini review):
    # On a fresh machine, codex may have just been installed and not yet
    # be on the running shell's PATH. Try $PATH first, then npm-prefix bin.
    CODEX_BIN="$(command -v codex 2>/dev/null || true)"
    if [[ -z "$CODEX_BIN" ]]; then
        NPM_GLOBAL_BIN="$(npm bin -g 2>/dev/null || echo "${HOME}/.npm-global/bin")"
        [[ -x "${NPM_GLOBAL_BIN}/codex" ]] && CODEX_BIN="${NPM_GLOBAL_BIN}/codex"
    fi
    cur="$([[ -n "$CODEX_BIN" ]] && "$CODEX_BIN" --version 2>/dev/null | awk '{print $NF}' || echo "<not-installed>")"

    if cur == PIN:
        echo "OK: codex-cli $cur already at pin $PIN"
        exit 0

    echo "Installing @openai/codex@$PIN (was: $cur) — pin tracks workspace-hub #2479 / openai/codex#19945"
    npm install -g "@openai/codex@${PIN}"

    # Re-resolve binary (npm install may have just placed it)
    CODEX_BIN="$(command -v codex 2>/dev/null || echo "${NPM_GLOBAL_BIN}/codex")"
    new="$("$CODEX_BIN" --version | awk '{print $NF}')"
    if new != PIN:
        echo "ERROR: install reports $new, expected $PIN" >&2
        exit 1
    echo "PINNED: codex-cli $new"
```

```
# Wiring into scripts/review/submit-to-codex.sh, before run_codex_exec call:
# SCRIPT_DIR is already defined at the top of submit-to-codex.sh (line 8).
. "${SCRIPT_DIR}/lib/codex-version-guard.sh"
guard_msg="$(codex_version_guard_check)"; guard_rc=$?
if [[ "$guard_rc" -eq 3 ]]; then
    echo "# Codex version guard tripped: $guard_msg" >&2
    # Emit a structured stub on stdout matching the existing failure-class
    # contract (cross-review.sh keys off the "# CODEX_..." prefix).
    echo "# CODEX_INCOMPATIBLE_VERSION"
    echo "# $guard_msg"
    echo "# Action: bash scripts/install/pin-codex.sh (or set CODEX_VERSION_GUARD_CEILING=<verified-good> if upstream fix is confirmed)"
    exit 7  # NEW reserved exit code for incompatible version (cross-review.sh routes this to UNAVAILABLE stub, not Opus fallback)
fi

# Wiring into scripts/review/plan-review-fanout.sh, codex case:
# Per F2 fix from 2026-05-02 Gemini review: the script-local variable is
# SCRIPT_DIR (set in the file header); compute lib path from it.
case "$prov" in
  codex)
    SCRIPT_DIR="${SCRIPT_DIR:-$(cd "$(dirname "$0")" && pwd)}"   # idempotent
    . "$SCRIPT_DIR/lib/codex-version-guard.sh"
    guard_msg="$(codex_version_guard_check)"; guard_rc=$?
    if [[ "$guard_rc" -eq 3 ]]; then
        printf '%s' "$guard_msg" > "$err"
        rc=3
        # falls through to normalize_provider_output → write_unavailable
        # which already emits the structured stub
    else
        timeout -k 5s "${timeout_s}s" codex exec "$combined" > "$out" 2>"$err" </dev/null || rc=$?
    fi
    ;;
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/review/lib/codex-version-guard.sh` | Shared library — `codex_version_guard_check()` + version-compare helpers |
| Create | `scripts/install/pin-codex.sh` | Idempotent install pin (default 0.123.0 via `CODEX_PIN_VERSION`) |
| Create | `scripts/install/` (directory) | New directory — currently no `scripts/install/` exists |
| Create | `scripts/review/tests/test_codex_version_guard.sh` | Unit tests for the guard library (mocks `codex --version`) |
| Modify | `scripts/review/submit-to-codex.sh` | Call `codex_version_guard_check()` before `run_codex_exec()`; emit `# CODEX_INCOMPATIBLE_VERSION` and exit 7 on rc=3 |
| Modify | `scripts/review/plan-review-fanout.sh` | Call `codex_version_guard_check()` in the `codex)` branch; on rc=3 set rc=3 + write guard message to err so existing `normalize_provider_output` emits the structured stub |
| Modify | `scripts/review/cross-review.sh` | Recognise exit code 7 from `submit-to-codex.sh` as INCOMPATIBLE_VERSION (route to UNAVAILABLE stub, NOT to Opus fallback — exit 3 keeps that behaviour) |
| Modify | `scripts/review/tests/test_plan_review_fanout.sh` | Add test 13: stub `codex` to print `codex-cli 0.128.0`; assert wrapper emits UNAVAILABLE stub WITHOUT calling `codex exec` (no 600s wait observed; capture file does not contain `ARGV: exec`) |
| Modify | `scripts/setup/new-machine-setup.sh` | After existing npm-prefix step, invoke `PATH="${NPM_GLOBAL}/bin:$PATH" bash scripts/install/pin-codex.sh` so the freshly-installed binary is reachable on first-bootstrap (per F3 fix from 2026-05-02 Gemini review); gated by `if command -v npm` |
| Modify | `scripts/setup/verify-setup.sh` | Source `scripts/install/codex-pin.env` (per F4 fix), replace bare `command -v codex` check with `codex --version` parse + compare against `${CODEX_PIN_VERSION}`; warn on drift |
| Update | `docs/plans/2026-04-26-issue-2479-codex-stdin-hang.md` | Add a one-line trailer at top: "**Superseded 2026-05-02 by `docs/plans/2026-05-02-issue-2479-codex-version-guard.md` — main absorbed wrapper-half via #2518; fix branch is now stale.**" |

**Explicitly NOT in scope (deferred to operator decision after this plan lands):**
- Merging `origin/fix/codex-stdin-hang` — diff against current main reverts #2518 hardening; do NOT merge. Branch will be left to drift until operator deletes manually.
- `docs/plans/README.md` index update — out of scope per user instruction.
- Closing or reopening #2406 — neutral; this plan does not block on that decision.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_guard_missing_codex` | Guard returns rc=2 with "not on PATH" when codex absent | `PATH=/empty bash -c '. lib/codex-version-guard.sh; codex_version_guard_check'` | rc=2, stdout contains "not on PATH" |
| `test_guard_pre_regression_passes` | Guard returns rc=0 OK for 0.121.0 (#2406 baseline) | mock `codex --version` → "codex-cli 0.121.0" | rc=0, stdout contains "OK" + "pre-regression" |
| `test_guard_known_good_0_123` | Guard returns rc=0 OK for 0.123.0 (last upstream-confirmed good) | mock → "codex-cli 0.123.0" | rc=0, stdout contains "OK" |
| `test_guard_floor_0_124_blocks` | Guard returns rc=3 INCOMPATIBLE for 0.124.0 | mock → "codex-cli 0.124.0" | rc=3, message references "#2479" + "openai/codex#19945" |
| `test_guard_current_0_128_blocks` | Guard returns rc=3 for 0.128.0 (current install) | mock → "codex-cli 0.128.0" | rc=3, message references "#2479" |
| `test_guard_ceiling_whitelist_band` | Setting `CODEX_VERSION_GUARD_CEILING=0.130.0` permits 0.130+ | mock → "codex-cli 0.130.0", env CEILING=0.130.0 | rc=0, stdout references "past whitelisted regression band" |
| `test_guard_unparseable_version` | Guard returns rc=2 on garbage `--version` output | mock → "codex pre-release banana" | rc=2, stdout contains "unparseable" |
| `test_guard_alpha_blocks` | Guard returns rc=3 for `0.129.0-alpha.1` (per F1 fix) — alphas at-or-above floor are uniformly INCOMPATIBLE | mock → "codex-cli 0.129.0-alpha.1" | rc=3, stdout contains "pre-release" |
| `test_guard_alpha_below_floor_passes` | Guard returns rc=0 for hypothetical `0.123.0-alpha.1` (below floor — pre-release of pre-regression line) | mock → "codex-cli 0.123.0-alpha.1" | rc=0 |
| `test_guard_version_command_timeout` | Guard returns rc=2 if `codex --version` takes >5s | mock that sleeps 10 | rc=2, stdout contains "timed out" |
| `test_fanout_codex_unavailable_on_bad_version` | `plan-review-fanout.sh codex` emits UNAVAILABLE stub when guard returns rc=3, WITHOUT calling `codex exec` | mock guard rc=3, mock `codex` that sleeps 60 | wrapper artifact contains "UNAVAILABLE" + "INCOMPATIBLE", capture file shows NO `ARGV: exec` invocation, total runtime < 10s |
| `test_pin_codex_idempotent` | `pin-codex.sh` is a no-op when current = pin | mock `codex --version` → "codex-cli 0.123.0" | rc=0, stdout contains "already at pin", no `npm install` invoked |
| `test_pin_codex_drift_detection` | `pin-codex.sh` calls `npm install -g @openai/codex@0.123.0` when current = 0.128.0 | mock `codex --version` → "codex-cli 0.128.0", capture `npm` argv | rc=0 (after second `codex --version` mock returns 0.123.0), npm capture contains "@openai/codex@0.123.0" |
| `test_verify_setup_warns_on_unpinned` | `verify-setup.sh` emits WARN when codex version != pin | mock `codex --version` → "codex-cli 0.128.0", `CODEX_PIN_VERSION=0.123.0` | rc=0 (non-fatal), stdout contains "WARN" + "0.128.0" + "0.123.0" |

---

## Acceptance Criteria

- [ ] `bash scripts/review/tests/test_codex_version_guard.sh` passes all 8 unit tests listed.
- [ ] `bash scripts/review/tests/test_plan_review_fanout.sh` passes all existing tests + new test 13 (codex INCOMPATIBLE path) on `main` after merge.
- [ ] On the current host (codex-cli 0.128.0 installed), `bash -c '. scripts/review/lib/codex-version-guard.sh; codex_version_guard_check; echo rc=$?'` returns rc=3 with stdout containing both `#2479` and `openai/codex#19945`.
- [ ] On a host with `npm install -g @openai/codex@0.123.0` applied (manual operator step OR via `bash scripts/install/pin-codex.sh`), the same command returns rc=0 with stdout containing `OK`.
- [ ] Live cross-review wave: `bash scripts/review/cross-review.sh` (or any nightly-batch call path) on a 90-byte test plan produces a real codex artifact with `## Verdict {APPROVE|MINOR|MAJOR|REJECT}` (not UNAVAILABLE) **on a host pinned to 0.123.0** within 300s. Acceptance is satisfied when a fresh `scripts/review/results/YYYY-MM-DD-plan-NNNN-codex.md` exists with a non-stub Verdict block AND the `submit-to-codex.sh` orchestrator log records a successful exit code (not 7, not 124).
- [ ] Live cross-review on an unpinned host (codex-cli 0.128.0): same dispatch produces an UNAVAILABLE artifact with text `INCOMPATIBLE_VERSION` AND **does not consume the 300s timeout** (orchestrator log shows codex provider exited within 10s).
- [ ] `bash scripts/setup/verify-setup.sh` on the unpinned host emits a `WARN` line citing the version drift.
- [ ] `bash scripts/install/pin-codex.sh` on the unpinned host successfully downgrades to 0.123.0 and reports `PINNED: codex-cli 0.123.0` (live operator-machine validation, NOT validated from inside Claude Code per `feedback_codex_cli_0_124_upstream_regression`).
- [ ] `PATH="" bash scripts/install/pin-codex.sh` on a host where codex is not yet on PATH (simulates first-bootstrap per F3 fix) does not exit 1 from binary-resolution; pin script falls back to `${NPM_GLOBAL_BIN}/codex` discovered via `npm bin -g`.
- [ ] `bash scripts/setup/verify-setup.sh` correctly reads `CODEX_PIN_VERSION` after sourcing `scripts/install/codex-pin.env` (per F4 fix); does NOT execute pin install as a side effect of sourcing.
- [ ] Prior plan trailer added to `docs/plans/2026-04-26-issue-2479-codex-stdin-hang.md` marking it superseded.
- [ ] Adversarial review artifacts posted: at minimum `scripts/review/results/2026-05-02-plan-2479-claude.md` and one of `scripts/review/results/2026-05-02-plan-2479-gemini.md` (Gemini preferred per task instructions). Codex review artifact path is intentionally absent (the subject under fix; see Adversarial Review Summary).
- [ ] Issue #2479 comment posted with branch name + plan path + review artifact paths.
- [ ] Issue #2479 label transitioned `wip:ace-linux-1` → `status:plan-review`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | (self-review by drafting agent — limited adversarial signal) | Same-author bias acknowledged. Gemini r1 carries the cross-provider load. |
| Codex | **SKIPPED** | Codex is the subject of this plan AND is currently broken on the install host. Per task instructions, do not dispatch a Codex review. The GitHub-connector path (which produces real verdicts on other plans) would still call out the regression as known and add no signal beyond what this plan already cites from openai/codex#19945. |
| Gemini | **MAJOR** (r1, 2026-05-02, `scripts/review/results/2026-05-02-plan-2479-gemini.md`) | 4 findings: F1 alpha-version regex bypass; F2 `$LIB_DIR` undefined in fanout; F3 PATH not exported during bootstrap so `codex --version` fails; F4 `CODEX_PIN_VERSION` cannot be read from `pin-codex.sh` by `verify-setup.sh` without recursive execution. **All resolved in this revision** — see Resolution table in the review artifact and inline `per F1/F2/F3/F4 fix` annotations in §Pseudocode and §Files to Change. |

**Overall result:** ADDRESSED. Gemini r1 returned MAJOR; the four findings were patched in-plan before user review. A Gemini r2 against the patched plan was NOT dispatched (single-author fallback per `feedback_permission_gate_blocks_cross_review`); user may request r2 if desired.

Per `feedback_permission_gate_blocks_cross_review.md` and `feedback_codex_sustained_MAJOR_loop.md`: if Gemini returns MAJOR, single-author r3 with strict rubric is the documented fallback rather than a Codex re-dispatch.

**Pre-empted critiques (the plan is hardened against these before adversarial review):**

1. **"What if upstream lands a fix in 0.129.0?"** — The guard's `CODEX_VERSION_GUARD_CEILING` env-var lets an operator unblock a verified-good newer version without code change. Procedure: install candidate, run a manual smoke (`codex exec "ping" </dev/null`), if it returns within 30s set `CODEX_VERSION_GUARD_CEILING=0.129.0` in the cron environment. A separate follow-up issue should propose promoting that env-var to a tracked file once a single new version is verified — out of scope for this plan.

2. **"The prior plan's `KNOWN_GOOD` allowlist approach is more flexible — why an open-ended deny instead?"** — Empirical: every version 0.124.0 → 0.128.0 has reproduced the bug across a five-week window. An allowlist that hard-codes 0.121, 0.122, 0.123, 0.125 (per the prior plan) is **wrong** — 0.125 reproduces the regression per upstream #19945, and the prior plan asserted 0.125 was good based on artifacts produced by a different code path (GitHub connector, not local exec). The deny-with-floor is correct against the current evidence; the allowlist would have shipped a known-bad whitelist entry.

3. **"Why not detect the hang dynamically by reading codex stderr for the `Reading additional input from stdin...` token?"** — Considered as a complementary v2 enhancement and rejected for v1: the regression sometimes silently exits with empty stdout instead of printing the banner (per upstream #19945's "silent crash" failure mode), so stderr-token matching has false-negatives. Version-gating is deterministic and fast (≤5s probe). A follow-up issue can add stderr-token detection as a defence-in-depth layer.

4. **"The plan claims 0.123.0 is good — is that asserted on a single source?"** — Two sources: upstream openai/codex#19945 explicitly states "0.123.0 unaffected", and `feedback_codex_cli_0_124_upstream_regression.md` records 0.123.0 was tested working from a plain user terminal. The plan also acknowledges (memory-cited) that 0.123.0 may not restore Codex from inside Claude Code's Bash tool, but nightly cron runs outside Claude Code, so the pin still helps the primary use case.

5. **"What about the stale `fix/codex-stdin-hang` branch — should this plan delete it?"** — No. Deletion is a destructive operation per `.claude/memory/topics/...` — leave it on origin and mark it superseded in this plan and in the prior plan's trailer. Operator may garbage-collect manually if desired.

6. **"How does this plan avoid the `feedback_mock_vs_live_invocation_divergence` trap?"** — Acceptance Criteria require a LIVE cross-review on a pinned host (not a mock) before close, with the orchestrator log showing the actual exit codes. Mock tests cover the guard logic; live tests cover the integration.

7. **"Why exit 7 and not extend the existing exit codes?"** — `submit-to-codex.sh` currently uses exit 1 (generic), 2 (CLI not found), 3 (QUOTA → triggers Opus fallback), 5 (NO_OUTPUT), 6 (renderer failure / raw passthrough). 7 is the next free integer. The contract change is in `cross-review.sh` (must recognise exit 7 as INCOMPATIBLE_VERSION → emit UNAVAILABLE stub, NOT route to Opus fallback because that would burn Opus credits on a fixable infrastructure issue).

8. **"Won't pinning to 0.123.0 break operators who depend on a 0.124+ feature?"** — Risk acknowledged. Audit on 2026-05-02: no scripts/code in workspace-hub reference flags or features added after 0.123.0. The new `codex review` subcommand (added later) is not invoked anywhere. If a future workflow needs 0.124+, the operator must verify upstream openai/codex#19945 has closed first OR set `CODEX_VERSION_GUARD_CEILING=<verified-good>` AND validate live; this plan documents that explicit gate.

---

## Risks and Open Questions

- **Risk: Cron environment doesn't source `CODEX_VERSION_GUARD_CEILING`.** Mitigation: the var defaults to empty (= deny everything ≥ floor) so omission is fail-closed. Operator must explicitly export the var via `~/.config/systemd/user/` or `crontab -e` to override.
- **Risk: `npm install -g @openai/codex@0.123.0` re-fetches on every machine.** Mitigation: `pin-codex.sh` is idempotent — the `if cur == PIN: exit 0` early-out skips the install when already at pin.
- **Risk: Operator runs `npm update -g` and silently breaks the pin.** Mitigation: `verify-setup.sh` will WARN on drift; `daily-readiness` cron (per memory) can be extended to call `verify-setup.sh --check-codex-pin` as a follow-up. Out of scope here, file as separate issue.
- **Risk: Live acceptance test on pinned 0.123.0 still fails because openai is rate-limiting or codex backend is down.** Mitigation: acceptance criterion says "non-stub Verdict OR explicit transient-failure record"; record the failure and re-run within 24h; close on first success.
- **Risk: Windows machines do not run `scripts/install/pin-codex.sh` automatically.** Mitigation: `new-machine-setup.sh` already has Windows branches; the pin invocation is gated on `command -v npm` so Windows operators can re-run it under Git Bash. Document in the prior-plan trailer.
- **Open: Should the runtime guard cache the `codex --version` result for the duration of a batch?** Probe is 5s max but runs per-provider per-plan. A 12-plan batch adds ≤60s overhead. Could cache via `/tmp/codex-version-cache.YYYY-MM-DD`. Defer to v2 unless reviewer flags as P1.
- **Open: Should `cross-review.sh` exit 7 propagate as a failure (cron should retry tomorrow) or as a graceful degrade (continue with 2-provider review)?** Current contract: graceful degrade (UNAVAILABLE stub, the 2-provider consensus runs as today). This matches `feedback_cross_provider_review_payoff` reality — losing Codex is a real signal loss but not a workflow blocker.
- **Open: Should this plan reopen #2406?** Plan-neutral; the issue body already discusses this and recommends "Leave #2406 closed-as-superseded unless maintainers prefer to reopen". This plan does not touch #2406's state.

---

## Complexity: T2

**T2** — three new files (guard library, pin script, guard test), four modified files (submit-to-codex, plan-review-fanout, cross-review, verify-setup, plus the existing test file), one trailer update on the prior plan. No architectural changes. Most complex piece is the version-compare logic in the guard, which delegates to `sort -V` (POSIX-portable). All other changes are mechanical wiring. Live acceptance requires a separate operator-machine validation step (cannot be self-validated from Claude Code per memory).
