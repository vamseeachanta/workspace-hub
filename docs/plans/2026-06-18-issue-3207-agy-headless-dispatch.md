# Plan for #3207: agy headless dispatch wrapper (unblocked — agy 1.0.9 ships --print)

> **Status:** adversarial-reviewed (r1 Claude MAJOR → revised; agy arg-contract empirically confirmed)
> **Complexity:** T2
> **Date:** 2026-06-18
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3207
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-18-plan-3207-claude.md

> **Blocker cleared:** agy upgraded 1.0.8→**1.0.9**, now exposing `--print`/`-p` (run a
> single prompt non-interactively + print response), `--print-timeout`, and
> `--dangerously-skip-permissions`. Verified headless: `agy --print --print-timeout 60s "…"`
> returned a response (exit 0) this session.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/ai/run_agent.py` — `WRAPPERS = {codex, gemini}` (l.44-46); `dispatch_run()` (l.186-199) runs `bash <wrapper> --file <f> --prompt <p>` with a per-provider env branch (codex pops `CLAUDECODE` #2684; gemini sets `GEMINI_CLI_TRUST_WORKSPACE`). `resolve_capabilities()` (l.88-116) raises `UnsupportedCapabilityError` if any capability is `unsupported` for the provider — this is what fail-closes agy today (no agy key in bindings).
- Found: `scripts/review/submit-to-gemini.sh` — the structural template (arg parse `--file/--commit/--prompt`, `command -v` guard, timeout, `cd "$run_dir"`, logging to `logs/orchestrator/gemini/`). But it is **review-oriented**: invokes `gemini -p … --yolo --output-format json` and renders via `render-structured-review.py --provider gemini` (`_parse_gemini` expects JSON).
- Found: `config/agents/provider-capabilities.yaml` `capability_bindings` (l.24-48) — per-capability per-provider `{enforcement: enforced|advisory|unsupported}`; gemini is `advisory` for read/search/run/write/web, `unsupported` for gui_automation. **No `agy` rows** → agy unsupported everywhere → dispatch fail-closed.
- Found: `render-structured-review.py --provider choices=(claude, gemini, codex)` — no agy; expects provider JSON.

### Gaps identified
- agy not in `WRAPPERS`, no `dispatch_run` branch, no capability bindings, no headless pre-flight check.
- **agy `--print` emits freeform text, not JSON** (no `--output-format` flag) → agy cannot (yet) be a *structured-review* provider without a `_parse_agy` + prompt-for-schema. The issue's goal is **dispatch** ("agy dispatch literally prepends the routed skill"), which does not need the JSON review renderer.

### Evidence
- `agy --version` → 1.0.9; `agy --help` exposes `--print`, `-p`, `--print-timeout`, `--dangerously-skip-permissions` (verified 2026-06-18).
- Headless smoke: `agy --print --print-timeout 60s "…"` → exit 0 + text response (ran from repo cwd; agy read the workspace).
- `run_agent.py:204` `--provider … choices=sorted(WRAPPERS)` → adding agy to WRAPPERS makes it a valid `--provider`.

<!-- sources: issue + run_agent.py + submit-to-gemini.sh + provider-capabilities.yaml + render-structured-review.py + live agy probe = 6 -->

---

## Deliverable

agy becomes a first-class **dispatch** provider: `run_agent.py --provider agy` resolves capabilities (no longer fail-closed), prepends the routed skill, and runs the task through `agy --print` via `scripts/review/submit-to-agy.sh` — gated by a Level-2 headless pre-flight so the wrapper is never shipped able-to-fail.

---

## Design / Pseudocode

**Scope = DISPATCH (recommended), not structured-review.** agy `--print` is freeform; making it a review provider would need a JSON mode agy lacks + a `_parse_agy`. Out of scope (flagged); a follow-up if agy adds `--output-format`.

`scripts/enforcement/check-agy-headless-capability.sh` (Level-2 pre-flight):
```
command -v agy || { echo "agy not installed"; exit 0 }   # absent != failure (other boxes)
# r1-F7: anchor on the flag column (not a description mention of "--print"); capture stderr.
agy --help 2>&1 | grep -qE '^[[:space:]]+--print[[:space:]]' || { echo "agy lacks --print — keep unsupported"; exit 1 }
echo "agy headless (--print) present"; exit 0
```

**agy arg contract — EMPIRICALLY CONFIRMED (2026-06-18 probes), corrects r1-F1/F2/F6:**
- `--print` takes the prompt as its **VALUE** (`--prompt` is "Alias for --print"). `agy --print "<TEXT>" --print-timeout 60s` → returned exactly `PONG`. The draft's `agy --print --print-timeout 60s "<TEXT>"` is **WRONG** — `--print` binds to the literal `"--print-timeout"` (probe response fixated on that token). **Never** pass content via a trailing positional or `-p`/`--prompt`.
- `--print-timeout` is a **Go duration** (`60s`, default `5m0s`) — NOT integer seconds.
- agy **ignores stdin** (a piped marker was not seen) → content MUST ride the `--print` value (argv), so it is **ARG_MAX-bounded** (~2 MB). Cap content (e.g. 1 MB) and document; cannot offload to stdin like the gemini wrapper.

`scripts/review/submit-to-agy.sh` (dispatch wrapper; freeform text out, logged):
```
parse --file/--commit/--prompt   (wrapper's OWN --prompt = the routed task text from run_agent; fine)
AGY_CMD="${AGY_CMD:-agy}";  command -v "$AGY_CMD" || { echo "# agy CLI not found"; exit 2 }
# r1-F5: read content into a var BEFORE any cd (mirror submit-to-gemini.sh:106 ordering)
CONTENT="$(head -c "${AGY_MAX_BYTES:-1000000}" "$CONTENT_FILE")"     # cap < ARG_MAX (no stdin path)
INPUT_TEXT="$PROMPT"$'\n\n--- CONTENT ---\n'"$CONTENT"
run from a clean run_dir (mktemp -d), timeout(1) in seconds wrapping agy:
  timeout "${AGY_TIMEOUT_SECONDS:-300}" "$AGY_CMD" \
    --print "$INPUT_TEXT" \                       # prompt is --print's VALUE (confirmed)
    --print-timeout "${AGY_PRINT_TIMEOUT:-240s}" \  # Go duration
    --dangerously-skip-permissions >raw 2>err </dev/null   # stdin closed (agy ignores it; avoids any hang)
emit raw to stdout; log to logs/orchestrator/agy/<tag>-<ts>.log; exit on agy rc
```
(`--dangerously-skip-permissions` so headless never blocks on a permission prompt. `mktemp -d` cwd so agy doesn't scan/act on the live repo. `</dev/null` makes stdin deterministic — r1-F9.)

`run_agent.py`:
```
WRAPPERS["agy"] = REPO_ROOT/scripts/review/submit-to-agy.sh
dispatch_run(): add `stdin=subprocess.DEVNULL` to the subprocess.run call (deterministic for all
    providers; agy ignores stdin anyway). No env-pop needed for agy (probe ran clean; not codex's #2684).
```

`config/agents/provider-capabilities.yaml` capability_bindings — add `agy` per capability:
```
read_files/search_code/run_shell/write_files/web_search:  agy: {enforcement: advisory}
gui_automation:  agy: {enforcement: unsupported}
```
(advisory = agy can be dispatched these capabilities without native-tool enforcement, same posture as gemini. This is what flips resolve_capabilities from raising.)

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/enforcement/check-agy-headless-capability.sh` | Level-2 pre-flight: only promote agy when `--print` present |
| Create | `scripts/review/submit-to-agy.sh` | agy `--print` dispatch wrapper |
| Create | `tests/ai/test_run_agent_agy.py` | agy in WRAPPERS, resolve_capabilities no longer raises, dispatch wiring (agy stubbed — no quota burn) |
| Create | `tests/enforcement/test_check_agy_headless.sh` (or .py) | pre-flight detects/【rejects】 --print |
| Modify | `scripts/ai/run_agent.py` | WRAPPERS += agy; dispatch_run env branch |
| Modify | `config/agents/provider-capabilities.yaml` | agy capability_bindings (flip from unsupported) |
| Update | docs/plans/README.md | index |

---

## TDD Test List

| Test | Verifies | Expected |
|---|---|---|
| test_agy_in_wrappers | agy is a valid --provider | "agy" in WRAPPERS |
| test_resolve_capabilities_agy_not_unsupported | bindings flip agy | no UnsupportedCapabilityError for a read/search/run agent |
| test_dispatch_builds_agy_command | dispatch prepends skill + targets the wrapper | cmd = bash submit-to-agy.sh --file … --prompt "<skill>…" |
| test_dispatch_run_agy_stubbed | dispatch_run invokes the wrapper (agy stubbed via AGY_CMD=fake) | exit_code/stdout plumbed; NO real agy call |
| test_check_agy_headless_detects_print | pre-flight sees --print (column-anchored) | exit 0 |
| test_check_agy_headless_rejects_when_absent | simulated agy without --print | exit 1 |
| test_submit_to_agy_missing_cli | agy absent | exit 2 + message (no crash) |
| test_submit_to_agy_invocation_shape (r1-F1/F2) | AGY_CMD=arg-recorder stub asserts the REAL flag order: `--print "<INPUT>" --print-timeout <godur> --dangerously-skip-permissions`; prompt is `--print`'s value, never a trailing positional, never `-p`/`--prompt` | recorded argv matches |
| test_every_binding_has_agy (r1-F3) | iterate `capability_bindings` keys; each has an `agy` enforcement (no future fail-closed gap) | all present |

Real `agy --print` is NOT called in unit tests (quota + nondeterminism): stub via `AGY_CMD=<arg-recorder script>` that records argv + echoes canned output, so the flag-assembly codepath (F1/F2 shape) IS exercised. **Pre-merge acceptance gate (r1-F7/F9):** one real `agy --print` smoke (recorded in the PR) — the only thing that confirms live arg semantics end-to-end (the probe already returned `PONG` for the corrected shape).

---

## Acceptance Criteria

- [ ] `agy --help` headless confirmed by `check-agy-headless-capability.sh` (else stays blocked)
- [ ] `submit-to-agy.sh` runs `agy --print`; `run_agent.py --provider agy` dispatches with the routed skill prepended
- [ ] `agy` capability bindings added; `resolve_capabilities` no longer fail-closes agy for advisory caps
- [ ] Tests green (agy stubbed); `uv run pytest tests/ai/test_run_agent_agy.py -v` + the pre-flight test
- [ ] No regression to codex/gemini dispatch
- [ ] Review artifact posted

---

## Adversarial Review Summary

**r1 — Claude (adversarial subagent), 2026-06-18:** verdict **MAJOR**. Findings + resolution (F1/F2/F6 confirmed by live agy probes):

| # | Sev | Finding | Resolution |
|---|---|---|---|
| F1 | MAJOR | `--prompt` is an alias for `--print`; draft passed the prompt as a trailing positional → agy binds it to `"--print-timeout"` (probe confirmed: response fixated on that token) | invocation corrected: `--print "<INPUT>"` (prompt is the flag VALUE), no positional, no `-p`/`--prompt`; `--` not needed since value follows the flag; `test_submit_to_agy_invocation_shape` asserts it |
| F2 | MAJOR | `--print-timeout` is a Go duration (`5m0s`), not int seconds | pinned `240s` (Go dur); outer `timeout(1)` stays int seconds — both documented |
| F6 | MAJOR | content as a single argv is ARG_MAX-bounded; agy ignores stdin (probe: piped marker unseen) → can't offload to stdin like gemini | cap content `head -c 1000000` (< 2 MB ARG_MAX), documented |
| F3 | MINOR | future capability added without an agy row silently fail-closes | `test_every_binding_has_agy` iterates all binding keys |
| F5 | MINOR | must read file into var BEFORE `cd mktemp` | mandated (mirror submit-to-gemini.sh:106) |
| F7 | MINOR | pre-flight grep matched a description mention | anchored to the flag column `^\s+--print\s`, `2>&1` |
| F9 | MINOR | dispatch_run stdin under capture_output could hang | `stdin=subprocess.DEVNULL` + `</dev/null` in wrapper |
| F10 | INFO | `advisory` is the only correct class (agy has no harness-gateable native tools) | kept advisory |

**Probes (this session):** `agy --print "Reply one word: PONG" --print-timeout 60s` → `PONG` (exit 0); piped-stdin marker NOT echoed (stdin ignored); draft's flag order produced off-topic output (F1 reproduced).

**r2 — Codex:** UNAVAILABLE (env timeout, repeated this session).

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (plan) | MAJOR→addressed | arg-contract bugs F1/F2/F6 confirmed+fixed via live probes; coverage/stdin/grep hardened |

**Code-stage r3 — Claude (adversarial subagent), 2026-06-18:** verdict **APPROVE** (2 MINOR). All 8 attack vectors clean against the live system (rc capture + empty-array expansion, content-cap single-read, argv quoting safety, YAML validity, stdin=DEVNULL safe for codex/gemini, pre-flight grep correct vs real agy, tests genuine, fail-closed coverage retained). Applied: r3 finding 2 — added an **untrusted-content boundary + preamble** to submit-to-agy.sh (prompt-injection parity with submit-to-gemini.sh; agy is Gemini-backed). Deferred (cosmetic): >1MB `head -c` boundary mojibake (matches gemini precedent). **Live smoke:** real `submit-to-agy.sh` dispatched a buggy `add()` → agy returned the correct defect ("subtracts b from a"), exit 0. 22 tests pass.

**r2 — Codex:** UNAVAILABLE (env timeout, repeated this session).

---

## Risks and Open Questions

- **Open (approval):** scope = **dispatch-only** (recommended; matches the issue goal + agy's freeform `--print`). Alternative: also wire agy as a structured-review provider (prompt-for-JSON + `_parse_agy` + renderer `--provider agy`) — bigger, depends on agy honoring a schema via `--print`; propose as a follow-up.
- **Risk — quota:** agy/Gemini quota is limited (TUI `/usage`); tests must stub agy. A real dispatch consumes quota — document a single manual smoke, don't run agy in CI.
- **Risk — agy reads/acts on cwd:** the smoke showed agy scanning the workspace. Mitigate by running the wrapper from `mktemp -d` + `--dangerously-skip-permissions` so a headless dispatch can't prompt or mutate the live tree unexpectedly.
- **Risk — stdin-hang under Claude-Code Bash (#2684 class):** codex needs `CLAUDECODE` popped; agy's smoke ran fine under Claude-Code Bash, so likely unaffected — verify in the dispatch_run branch and pop if needed.
- **Risk — `--dangerously-skip-permissions`:** appropriate for headless dispatch but powerful; scope it to the wrapper (not exported globally) and note it.
- **Resolved (empirically, this session):** headless blocker (agy 1.0.9 `--print`); the agy arg contract — prompt is `--print`'s value (`agy --print "<TEXT>" --print-timeout 60s` → `PONG`); `--print-timeout` = Go duration; agy ignores stdin → argv delivery capped < ARG_MAX; dispatch_run stdin made deterministic (`DEVNULL`).

## Complexity: T2

**T2** — new wrapper + pre-flight + run_agent wiring + bindings + tests; built on #3190's WRAPPERS substrate. Review = Claude inline (+ Codex if env permits; it has timed out repeatedly this session).
