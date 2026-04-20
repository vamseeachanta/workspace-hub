# Plan for #2406: fix(review) — submit-to-codex.sh hangs on "Reading additional input from stdin" for substantial plan files

> **Status:** adversarial-reviewed (v2 — iter-1 Codex+Gemini MAJOR addressed)
> **Complexity:** T2
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2406
> **Review artifacts:** scripts/review/results/2026-04-20-plan-2406-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/review/submit-to-codex.sh:162-180` — `run_codex_exec()` passes the full prompt as a positional argv to `codex exec "$prompt_text"` in all three dispatch branches (`timeout`, `perl alarm`, bare). All three branches share the hang.
- Found: `scripts/review/submit-to-codex.sh:215-227` — initial size guard: if `payload_chars > CODEX_MAX_PROMPT_CHARS` (default 120 000), **pre-truncate** `CONTENT_TEXT` to `CODEX_COMPACT_RETRY_CHARS` (default 24 000) and rebuild `prompt_for_run`. This is truncation, **not rejection**; dispatch proceeds with the truncated prompt.
- Found: `scripts/review/submit-to-codex.sh:229-247` — compact-retry fallback: after `run_codex_exec "$prompt_for_run"`, if `exec_exit != 0` **OR** `raw_file` is empty, retry once with a prompt truncated to `CODEX_COMPACT_RETRY_CHARS`. The retry is triggered by **any first-dispatch failure including timeout** — so today's observed hang-exit-124 case triggers the retry, and the retry also dispatches via the same buggy argv path. Both calls (line 230 and line 246) share `run_codex_exec`, so fixing that function fixes both.
- Found: `scripts/review/submit-to-gemini.sh` — Gemini dispatch uses a different CLI, not affected. Confirmed via Gemini reviewing 4 prompts this session without hang.
- Found: `tests/review/test-submit-scripts.sh` (320 lines) — existing mock-based test harness using `make_mock` to replace CLI binaries on PATH. Existing test-case count: 22 (per `grep -cE "^# ── T[0-9]+:"` on 2026-04-20). T07/T24/T25 already cover `submit-to-codex.sh`. Pattern is reusable for a new argv-size regression test.
- Gap: no existing test covers the argv-vs-stdin dispatch path; no test with a large prompt fixture.

### Standards

Not applicable — infrastructure script bug fix, no engineering standards involved.

### Operating-model compliance (explicit N/A rationale)

Per reviewer request in iter-1 (Codex): each operating-model section is explicitly evaluated below, not silently skipped.

| Section | Applies? | Rationale |
|---|---|---|
| §2 ownership (L<n> classification) | **No** | This plan modifies `scripts/review/` and `tests/review/` — harness infrastructure, not the document-intelligence corpus. Operating-model layer classes (L0–L5) govern knowledge/intelligence artifacts, not bash scripts. No ownership invention. |
| §3 identity / `doc_key` / `sha256:` namespace | **No** | `doc_key` identity applies to documents in the doc-intelligence corpus (`knowledge/`, `docs/document-intelligence/`, and ingested standards). This plan is a harness bug fix; new artifacts are a bash script patch and a pytest-style fixture. No `doc_key` required. |
| §4 flow rules | **No** | No durable-store flows modified. Plan file itself lives at `docs/plans/` which is the governance-plan tier (per skill "Safe paths"), not a doc-intelligence flow endpoint. |
| §7 cross-machine tier rules | **Yes (partial)** | Test fixture `tests/review/fixtures/codex-large-prompt.txt` is git-tracked → tier-1 durable metadata. Mock-generated stdin/argv logs in tests are tier-5 transient temp files under `$(mktemp -d)` → correctly scoped. No cross-machine mount dependency. ✓ |
| §8.1 frontmatter authority | **No** | No wiki or knowledge-domain content created. |

### LLM Wiki pages consulted

No relevant wiki pages — this is a review-harness bug, not a domain-knowledge change.

### Documents consulted

- `.planning/handoffs/2026-04-20-doc-intel-planning-handoff.md` — "Action 1" explicitly recommends this fix first; rationale: unblocks reliable Codex reviews for every downstream plan.
- Issue #2405 (cross-review sandbox repo access) — **related context, not a dependency.** #2405 addresses reviewer **verification** access (Class B self-circular "unverified" findings); #2406 addresses reviewer **dispatch** reliability. #2406 is executable independently of #2405 and can land first. The two together restore full cross-review quality, but neither blocks the other.
- `memory/feedback_codex_needs_pushed_artifact.md` — Codex sandbox reads from GitHub, not local filesystem. Informs test design: tests must not require live Codex API.
- `memory/feedback_cross_provider_review_payoff.md` — Codex finds non-overlapping defects from Claude and Gemini. Losing Codex reliably (current state) measurably weakens review quality; this fix has high leverage.
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` — mandates TDD step 6, plan-approval gate, adversarial review. Also mandates (Step 2) updating `docs/plans/README.md` index — that is why the README update is in-scope for this plan, not scope creep.

### Gaps identified

- Current `run_codex_exec` always puts the prompt on argv — the `codex exec [PROMPT]` arg. Per `codex exec --help`: **"If not provided as an argument (or if `-` is used), instructions are read from stdin."** When the caller orchestrating this script has a non-tty stdin that isn't explicitly redirected (e.g. the bash script is spawned from another agent), `codex` may block on stdin waiting for more data. That explains the "Reading additional input from stdin..." stall.
- No explicit stdin handling in `submit-to-codex.sh` — stdin inherits from the caller, which in orchestrated environments can be an unconsumed pipe.
- No automated regression: even after fix, a future refactor could re-introduce argv-path dispatch.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-20T19:47:00Z via `gh issue view`):
- `#2406` — OPEN — "fix(review): submit-to-codex.sh hangs on 'Reading additional input from stdin' for substantial plan files" (labels: bug, priority:high, cat:ai-orchestration, cat:harness, domain:document-intelligence)
- `#2405` — CLOSED — labels include both `status:plan-review` and `status:plan-approved` (state drift — not fixed here; flagged for follow-up)
- `#2403` — OPEN — `status:plan-approved`
- `#2402` — OPEN — `status:plan-approved` (handoff; plan drafted, review pending)

**File existence** (`ls -la` 2026-04-20T19:47:00Z):
- EXISTS: `scripts/review/submit-to-codex.sh`
- EXISTS: `scripts/review/submit-to-gemini.sh`
- EXISTS: `tests/review/test-submit-scripts.sh`
- EXISTS: `tests/review/fixtures/` (directory)
- MISSING (new — this plan creates): `tests/review/fixtures/codex-large-prompt.txt` (>24 000 chars for compact-retry path; >2 000 chars for argv-path repro)

**Line excerpts** (`sed -n 162,180p scripts/review/submit-to-codex.sh`):
```
  run_codex_exec() {
    local prompt_text="$1"
    if command -v timeout >/dev/null 2>&1; then
      timeout "$CODEX_TIMEOUT_SECONDS" "$CODEX_BIN" exec "$prompt_text" \
        --skip-git-repo-check \
        --output-schema "$schema_file" \
        --output-last-message "$raw_file" >/dev/null 2>"$err_file"
    elif command -v perl >/dev/null 2>&1; then
      perl -e 'alarm shift; exec @ARGV' "$CODEX_TIMEOUT_SECONDS" "$CODEX_BIN" exec "$prompt_text" \
        --skip-git-repo-check \
        --output-schema "$schema_file" \
        --output-last-message "$raw_file" >/dev/null 2>"$err_file"
    else
      "$CODEX_BIN" exec "$prompt_text" \
        --skip-git-repo-check \
        --output-schema "$schema_file" \
        --output-last-message "$raw_file" >/dev/null 2>"$err_file"
    fi
  }
```

**CLI contract** (`codex exec --help` 2026-04-20T19:47:00Z):
```
Arguments:
  [PROMPT]
      Initial instructions for the agent. If not provided as an argument (or if `-` is used),
      instructions are read from stdin. If stdin is piped and a prompt is also provided, stdin
      is appended as a `<stdin>` block
```

This confirms the CLI natively supports stdin input when the positional arg is `-` or omitted.

**Gap proofs**:
- `grep -n 'codex exec' scripts/review/submit-to-codex.sh` → 3 invocations (165, 170, 175), all pass `"$prompt_text"` positionally. No stdin redirection.
- `grep -n '< /dev/null\|printf.*| *codex' scripts/review/submit-to-codex.sh` → no matches (current script never redirects stdin).

<!-- Distinct sources consulted: issue #2406 body, issue #2405, issue #2403, issue #2402, script source (line excerpts), codex CLI help, existing test harness, 2 memory files, handoff doc, issue-planning-mode skill — count ≥ 10. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-20-issue-2406-codex-stdin-hang-fix.md` |
| Tests | `tests/review/test-submit-scripts.sh` (new cases T26/T27/T28) |
| Test fixture | `tests/review/fixtures/codex-large-prompt.txt` (new) |
| Implementation | `scripts/review/submit-to-codex.sh` (modify `run_codex_exec`) |
| Plan review — Claude | `scripts/review/results/2026-04-20-plan-2406-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-20-plan-2406-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-20-plan-2406-gemini.md` |
| Index update | `docs/plans/README.md` (new row for #2406) |

---

## Deliverable

`scripts/review/submit-to-codex.sh` that reliably dispatches any prompt (up to the existing 120 000-char guard) to `codex exec` without hanging on stdin, verified by a regression test in `tests/review/test-submit-scripts.sh` that uses a ≥20 000-char fixture prompt and a `codex` mock which asserts the prompt was delivered on stdin, not argv.

---

## Pseudocode

```
# NEW run_codex_exec contract:
#   - Input: prompt_text (any length up to CODEX_MAX_PROMPT_CHARS)
#   - Pipe prompt on stdin; pass `-` as the positional PROMPT argument
#   - This way the CLI's documented "read from stdin" path is used
#     deterministically, eliminating argv-size fragility.

run_codex_exec(prompt_text):
    if timeout available:
        printf '%s' "$prompt_text" \
          | timeout "$CODEX_TIMEOUT_SECONDS" "$CODEX_BIN" exec - \
              --skip-git-repo-check \
              --output-schema "$schema_file" \
              --output-last-message "$raw_file" \
              >/dev/null 2>"$err_file"
    elif perl available:
        printf '%s' "$prompt_text" \
          | perl -e 'alarm shift; exec @ARGV' \
              "$CODEX_TIMEOUT_SECONDS" "$CODEX_BIN" exec - \
              --skip-git-repo-check \
              --output-schema "$schema_file" \
              --output-last-message "$raw_file" \
              >/dev/null 2>"$err_file"
    else:
        printf '%s' "$prompt_text" \
          | "$CODEX_BIN" exec - \
              --skip-git-repo-check \
              --output-schema "$schema_file" \
              --output-last-message "$raw_file" \
              >/dev/null 2>"$err_file"
```

Notes on design choices:
- **Use `printf '%s' ...` not `echo`** — `echo` interprets backslashes on some platforms and appends a newline; `printf '%s'` passes bytes verbatim and matches prompt length exactly.
- **Explicit `-` positional** — per the CLI help, `-` means "read from stdin". Omitting the arg entirely also works, but `-` is documented and self-describing.
- **Preserve error-path handling** — existing `classify_codex_failure`, `exec_exit` capture, compact-retry, `check_uv_readiness` all remain unchanged; only the dispatch shape changes.
- **Compact retry path inherits fix** — the retry calls `run_codex_exec` too (line 246), so a single change covers both the initial and retry dispatch.
- **Pipefail semantics (documented explicitly per iter-1 Gemini finding):** the script runs with `set -euo pipefail` (line 6). The new pipeline `printf | codex` reports pipefail-rightmost-nonzero, so `run_codex_exec … || exec_exit=$?` captures codex's exit correctly. **SIGPIPE edge case:** if `codex` exits early, `printf` may receive SIGPIPE (exit 141). With `pipefail`, the pipeline would then return 141, masking codex's real exit. Mitigation: capture `${PIPESTATUS[1]}` immediately after the pipeline to always report codex's real exit, overriding any printf-SIGPIPE noise. Example shape:
  ```
  { printf '%s' "$prompt_text" | timeout … "$CODEX_BIN" exec - … >/dev/null 2>"$err_file"; } ; rc=${PIPESTATUS[1]}
  ```
  The `||` exit-capture idiom then becomes `run_codex_exec "$p"; exec_exit=$?` (always 0 from the wrapping function body unless we propagate `$rc`). Final implementation detail lives in code; tested by T27/T28 behavior.
- **Runtime codex-version compatibility probe:** before first dispatch, the fix adds a one-shot probe — `"$CODEX_BIN" exec --help 2>&1 | grep -q 'read from stdin'` — cached in a module-scope flag. If the probe fails (older codex without documented stdin support), fall back to the old argv path and log a one-time WARN to stderr recommending CLI upgrade. This preserves correctness on older installs.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/review/submit-to-codex.sh` | rewrite `run_codex_exec` (lines 162–180) to pipe prompt via stdin with `-` positional; add one-time codex-version probe and argv-path fallback; add `PIPESTATUS[1]` capture for SIGPIPE robustness. No change to error-classification, exit-code map, or compact-retry trigger logic. |
| Create | `tests/review/fixtures/codex-large-prompt.txt` | deterministic large-prompt fixture (24 000 chars = 400 × 60-char lines), reproducible via one-liner |
| Modify | `tests/review/test-submit-scripts.sh` | add T26 (argv must not contain full prompt), T27 (stdin delivers the prompt), T28 (compact-retry path also uses stdin), T29 (pipefail+SIGPIPE fidelity), T30 (version-probe fallback) |
| Update | `docs/plans/README.md` | add index row for #2406 (already landed in v1 commit a73ec66f6) |

---

## TDD Test List

Tests live in `tests/review/test-submit-scripts.sh` and use the existing `make_mock` harness. Each mocks `codex` with a shell script that records its argv and stdin to temp files, then asserts on them.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| T26: codex dispatch — argv does NOT contain full prompt | `run_codex_exec` does not inflate argv with large prompts | large-prompt fixture via `--file`, short prompt via `--prompt` | mock's recorded argv contains `exec` and `-` (or no positional) but NOT any substring of the fixture body |
| T27: codex dispatch — stdin DELIVERS the prompt | mock's stdin equals the constructed FULL_PROMPT exactly | same as T26 | `diff <(mock_stdin) <(expected_full_prompt)` is empty (ignoring trailing newline) |
| T28: compact-retry path uses stdin on BOTH calls | when first dispatch returns empty `raw_file`, retry still pipes via stdin | mock that returns empty `raw_file` on call 1, success on call 2; prompt length forces retry via `:0:CODEX_COMPACT_RETRY_CHARS` truncation path | call-1 and call-2 recorded invocations both show argv without body substring and stdin containing prompt content (call-2 with truncated content) |
| T29: pipefail + SIGPIPE exit-code fidelity | when codex exits 3 (quota) while printf still has unread buffer, exec_exit captured is 3, not 141 | mock codex: write minimal error to err_file, `exit 3` | `submit-to-codex.sh` exits 3 (QUOTA path), not 141 (SIGPIPE masked as pipeline exit) |
| T30: codex-version-probe fallback | on older codex without stdin support in help text, dispatch falls back to argv path and emits a one-time WARN | mock codex whose `exec --help` does NOT contain "read from stdin" | script uses argv path; stderr contains WARN about CLI upgrade; exit code matches argv-path behavior |

Test-writing order (Red → Green):
1. Write T26/T27/T28/T29/T30 first against the **current** buggy code. T26/T27/T28 fail (argv used); T29 may already pass (existing semantics); T30 fails (no fallback yet).
2. Apply the `run_codex_exec` fix including `PIPESTATUS[1]` capture and version probe.
3. Re-run suite — new tests pass; existing 22 cases still pass.
4. Run full `bash tests/review/test-submit-scripts.sh` to confirm no regression.

Fixture design for T26–T30:
- `tests/review/fixtures/codex-large-prompt.txt` generated deterministically: 400 lines × 60 chars each = 24 000 chars. Committed as a file so the test is reproducible on any machine. Generation one-liner (run once, commit result): `yes "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" | head -400 > tests/review/fixtures/codex-large-prompt.txt`.
- Mock `codex` script shape: `printf '%s\n' "$@" > "$ARGV_LOG"; cat > "$STDIN_LOG"; echo '{"verdict":"APPROVE","summary":"mocked","issues_found":[],"suggestions":[],"questions_for_author":[]}' > "$OUTPUT_LAST_MESSAGE"; exit "${MOCK_EXIT:-0}"`.
- The mock reads `--output-last-message` from its argv to know where to write the JSON. This mirrors codex's real behavior.

### Acceptance Criteria ↔ Test Traceability

Every acceptance criterion maps to at least one automated test or an explicit manual-verification step. Automated criteria are verified by `bash tests/review/test-submit-scripts.sh`; manual criteria are verified interactively and recorded as a closeout comment.

| AC | Test(s) | Kind |
|---|---|---|
| Fix makes `codex exec` receive prompt on stdin | T26, T27 | automated |
| Compact-retry path also uses stdin | T28 | automated |
| Pipefail+SIGPIPE does not mask codex exit code | T29 | automated |
| Older codex CLI falls back to argv path with WARN | T30 | automated |
| No change to exit-code semantics (existing 1/2 paths) | T01, T02, T03, T07, T24, T25 (existing) | automated |
| Exit-code semantics for 3/5/6 paths preserved (no new tests, but also not changed by fix) | none new — change is localized to dispatch shape | manual spot-check (closeout) |
| `docs/plans/README.md` index row exists | `grep -q '^| 2406 |' docs/plans/README.md` in closeout script | manual/shell |
| Three review artifacts posted to `scripts/review/results/` | `ls scripts/review/results/2026-04-20-plan-2406-*.md \| wc -l` ≥ 3 in closeout | manual/shell |
| **Live repro**: with the real codex CLI against the #2405 v3 plan, the fix completes within `CODEX_TIMEOUT_SECONDS` | live execution outside automated suite | manual only (live API) |

---

## Acceptance Criteria

Automated (pass/fail via `bash tests/review/test-submit-scripts.sh`):
- [ ] All **22 existing** test cases still pass (regression check).
- [ ] T26 passes: mock's recorded argv does not contain the fixture body.
- [ ] T27 passes: mock's recorded stdin equals the constructed FULL_PROMPT byte-for-byte (minus optional trailing newline).
- [ ] T28 passes: compact-retry path uses stdin on both call-1 and call-2.
- [ ] T29 passes: codex exit 3 propagates through the pipeline unmasked.
- [ ] T30 passes: older codex without stdin-help support falls back to argv path with WARN.

Manual / shell-check (documented in closeout comment):
- [ ] `docs/plans/README.md` contains a row starting with `| 2406 |`.
- [ ] `ls scripts/review/results/2026-04-20-plan-2406-*.md` shows ≥ 3 artifacts.
- [ ] Live repro: re-running the failing command from the issue body against `docs/plans/2026-04-20-issue-2405-cross-review-sandbox-repo-access.md` on the fixed branch completes within `CODEX_TIMEOUT_SECONDS` (returns structured review content or a classified failure, not a hang).

Exit-code map preserved (not newly tested; localized dispatch-shape change should not touch these paths):
- 1 = user error, 2 = CLI missing, 3 = quota, 5 = NO_OUTPUT, 6 = renderer fail.

---

## Adversarial Review Summary

| Provider | Verdict (iter-1) | Key findings |
|---|---|---|
| Claude (self) | MINOR | Test-count off (22, not 25); pipefail semantics undocumented; guard-interaction not called out; exit-code AC coverage partial |
| Codex | MAJOR | Compact-retry reasoning internally inconsistent; AC↔test traceability missing; #2405 dependency wording contradictory; operating-model §2/§4/§7/§8.1 checks absent; threat model missing; version-skew risk not mitigated. Plus Class B self-circular "unverified live-state" (resolves at #2405 implementation). |
| Gemini | MAJOR | Pipefail semantics unspecified; README-update AC lacks automated test; artifact identity not `sha256:`-namespaced. Plus Class B self-circular unverified claims. |

**Overall result (iter-1):** REVISE — addressed in v2.

Revisions made based on iter-1 review (v1 → v2):
- Fixed the compact-retry triggering logic description — retry fires on **any** first-dispatch failure, not only when the 120 000-char guard is defeated (Codex P1).
- Corrected "25 existing cases" → "22" (Claude P2).
- Added Operating-model compliance sub-table with explicit N/A rationale for §2/§3/§4/§7/§8.1 (Codex P1).
- Clarified that #2405 is **related context, not a dependency** — #2406 is executable independently (Codex P1).
- Justified README-update inclusion as a **skill-mandated** process step, not scope creep, citing `issue-planning-mode/SKILL.md` Step 2 (Codex P2).
- Added pipefail semantics + SIGPIPE edge case + `PIPESTATUS[1]` capture in the Pseudocode notes (Gemini + Claude P2).
- Added runtime codex-version-probe fallback in the Pseudocode notes to handle older CLIs without stdin-`-` documentation (Codex + Claude P2).
- Added T29 (pipefail+SIGPIPE fidelity) and T30 (version-probe fallback) to the TDD list.
- Added explicit AC ↔ Test traceability matrix separating automated from manual checks (Codex P1).
- Added Threat Model sub-section under Risks (Codex P2).

Class B findings (self-circular / reviewer-cannot-verify-live-state) acknowledged and carried forward:
- Codex's "unverified correctness-critical assertions" — identical category to the #2405 Class B convergent finding. Resolves when #2405 implementation lands its pre-verification attestation. v2 does not attempt to inline-satisfy it.
- Gemini's "cannot verify live GitHub issue states" — same category; same resolution path.

---

## Risks and Open Questions

- **Risk:** the hang could have a second root cause we haven't identified (e.g. codex checking for a TTY on fd 1 or 2). Mitigation: T26/T27/T28 mock-tests verify argv/stdin shape deterministically; manual live verification in AC list confirms real-world behavior. If hang persists after fix, re-open with trace data (`strace -f -o strace.log`) attached.
- **Risk:** the fix changes the prompt delivery path; it's possible codex's `<stdin>` block framing is subtly different from argv (e.g. extra wrapping). Mitigation: T27 compares the mock's stdin byte-for-byte with the expected prompt. If codex wraps differently, T27 will catch it before it hits production.
- **Risk:** the `-` positional arg is undocumented edge behavior in some codex versions. Mitigation: runtime version probe + argv-path fallback (T30). Pinned by CLI-help evidence for the current installed version.
- **Risk:** `CODEX_MAX_PROMPT_CHARS` guard behavior is unchanged by this fix — the pre-truncation logic still runs before `run_codex_exec`. Noted explicitly to prevent confusion during review.
- **Risk:** bash `printf '%s' "$prompt_text"` may hit a buffer limit on very long prompts. Mitigation: bash uses heap for variable storage; 5 MB max (already enforced at line 131 by `head -c 5000000`). Pipe writes in chunks from bash builtin's perspective; no documented failure mode below `ARG_MAX`.

### Threat model (added per iter-1 Codex finding)

| Surface | Current behavior | Fix behavior | Delta risk |
|---|---|---|---|
| PATH trust for `CODEX_BIN` | script trusts `command -v codex`; falls through to `${HOME}/.npm-global/bin/codex` | unchanged | none |
| Prompt content source | `$PROMPT` from `--prompt` argv, `$CONTENT_TEXT` from `--file` via `head -c 5M \| tr -d '\000'` | unchanged — same `$FULL_PROMPT` string, just delivered via a different channel (stdin vs argv) | none — same bytes, same sink |
| Argv exposure (ps/strings visibility) | full prompt visible in process-table `ps -ef` — any user on the host can read current-user prompts for the lifetime of the codex invocation | prompt removed from argv; only flags + `-` visible in `ps`. **Improvement.** | **reduced** — sensitive plan content no longer leaks via process table |
| stdin pipe content | unconsumed inherited stdin could block codex (the bug) | explicit `printf | codex exec -` — codex receives prompt then EOF | **eliminated** — hang path closed |
| `$raw_file` / `$err_file` temp files | `mktemp` under `/tmp`, cleaned on EXIT via trap (line 145) | unchanged | none |
| Renderer invocation | `uv run --no-project python "$RENDERER"` on raw file | unchanged | none |
| Mock-based test PATH injection | tests prepend `MOCK_DIR` to PATH inside subshell; cleaned on EXIT | unchanged — mocks never touch real codex | none |

**Security improvement note:** moving the prompt out of argv is a net privacy improvement — plan contents and adversarial prompts may include sensitive repo details (paths, issue numbers, internal filenames) that previously leaked to anyone with `ps` access during review dispatch.

### Open questions

- **Open:** should we also add a warning when `CODEX_MAX_PROMPT_CHARS` is exceeded and the compact retry path is chosen? Currently silent. Flag for user — outside the scope of this issue, but trivial follow-up.

---

## Complexity: T2

**T2** — bug fix in a single file with required TDD coverage + a new test fixture. Not T1 because it introduces a new test pattern (argv-vs-stdin assertion) that will be reused for future reviewer-CLI changes; not T3 because there is no architecture change or cross-file design.
