# Plan for #2406: fix(review) — submit-to-codex.sh hangs on "Reading additional input from stdin" for substantial plan files

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2406
> **Review artifacts:** scripts/review/results/2026-04-20-plan-2406-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/review/submit-to-codex.sh:162-180` — `run_codex_exec()` passes the full prompt as a positional argv to `codex exec "$prompt_text"` in all three dispatch branches (`timeout`, `perl alarm`, bare). All three branches share the hang.
- Found: `scripts/review/submit-to-codex.sh:229-247` — one compact-retry fallback re-invokes `run_codex_exec` with a truncated (≤24 000-char) prompt via the same argv path. The retry therefore inherits the argv-vs-stdin hazard, but only for prompts large enough to first defeat the 120 000-char initial guard at line 216.
- Found: `scripts/review/submit-to-gemini.sh` — Gemini dispatch uses a different CLI, not affected. Confirmed via Gemini reviewing 4 prompts this session without hang.
- Found: `tests/review/test-submit-scripts.sh` (320 lines) — existing mock-based test harness using `make_mock` to replace CLI binaries on PATH. T07/T24/T25 already cover `submit-to-codex.sh`. Pattern is reusable for a new argv-size regression test.
- Gap: no existing test covers the argv-vs-stdin dispatch path; no test with a large prompt fixture.

### Standards

Not applicable — infrastructure script bug fix, no engineering standards involved.

### LLM Wiki pages consulted

No relevant wiki pages — this is a review-harness bug, not a domain-knowledge change.

### Documents consulted

- `.planning/handoffs/2026-04-20-doc-intel-planning-handoff.md` — "Action 1" explicitly recommends this fix first; rationale: unblocks reliable Codex reviews for every downstream plan.
- Issue #2405 (cross-review sandbox repo access) — related but distinct: #2405 is about reviewer **verification** access, #2406 is about reviewer **dispatch** reliability. Both must land before cross-provider review is trustworthy again.
- `memory/feedback_codex_needs_pushed_artifact.md` — Codex sandbox reads from GitHub, not local filesystem. Informs test design: tests must not require live Codex API.
- `memory/feedback_cross_provider_review_payoff.md` — Codex finds non-overlapping defects from Claude and Gemini. Losing Codex reliably (current state) measurably weakens review quality; this fix has high leverage.
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` — mandates TDD step 6, plan-approval gate, adversarial review.

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

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/review/submit-to-codex.sh` | rewrite `run_codex_exec` (lines 162–180) to pipe prompt via stdin; no other behavior change |
| Create | `tests/review/fixtures/codex-large-prompt.txt` | deterministic large-prompt fixture (≥20 000 chars, reproducible) |
| Modify | `tests/review/test-submit-scripts.sh` | add T26 (argv must not contain full prompt), T27 (stdin delivers the prompt), T28 (compact-retry path also uses stdin) |
| Update | `docs/plans/README.md` | add index row for #2406 |

---

## TDD Test List

Tests live in `tests/review/test-submit-scripts.sh` and use the existing `make_mock` harness. Each mocks `codex` with a shell script that records its argv and stdin to temp files, then asserts on them.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| T26: codex dispatch — argv does NOT contain full prompt | `run_codex_exec` does not inflate argv with large prompts | large-prompt fixture via `--file`, simple prompt via `--prompt` | the mock's recorded argv contains `exec` and `-` but not the 20 000-char payload body |
| T27: codex dispatch — stdin DELIVERS the prompt | mock's stdin equals the constructed FULL_PROMPT | same as T26 | `diff <(mock_stdin) <(expected_full_prompt)` is empty (ignoring trailing newline) |
| T28: compact-retry also uses stdin | when first call returns empty, retry still pipes via stdin | mock that returns empty on first call, success on second; prompt > `CODEX_COMPACT_RETRY_CHARS` | both invocations show empty-prompt-argv and non-empty stdin |

Test-writing order (Red → Green):
1. Write T26/T27/T28 first against the **current** buggy code. They should fail because current script puts the prompt on argv.
2. Apply the `run_codex_exec` fix.
3. Re-run suite — T26/T27/T28 pass; existing T07/T24/T25 still pass.
4. Run full `bash tests/review/test-submit-scripts.sh` to confirm no regression.

Fixture design for T26/T27:
- `tests/review/fixtures/codex-large-prompt.txt` generated deterministically: 400 lines × 60 chars each = 24 000 chars. Committed as a file so the test is reproducible on any machine.
- Mock `codex` script: `printf '%s' "$*" > $ARGV_LOG; cat > $STDIN_LOG; echo '{"verdict":"APPROVE","summary":"mocked","issues_found":[],"suggestions":[],"questions_for_author":[]}' > "$raw_file"; exit 0`

---

## Acceptance Criteria

- [ ] `bash tests/review/test-submit-scripts.sh` passes with 3 new T26/T27/T28 cases green and all 25 existing cases still green.
- [ ] Manual live repro: on a `git` checkout that reproduces the original hang (e.g. the command in the issue body against `docs/plans/2026-04-20-issue-2405-cross-review-sandbox-repo-access.md`), the fixed script completes within `CODEX_TIMEOUT_SECONDS` (returning real review content or real error, not hanging). This step is **manual live verification** — runs against the real Codex CLI but is not part of the automated regression suite.
- [ ] `codex exec` receives the prompt on stdin and `-` on argv (verified in T26/T27).
- [ ] No change to error-classification behavior (T07/T24/T25 still pass).
- [ ] No change to exit-code semantics (1 = user error, 2 = CLI missing, 3 = quota, 5 = NO_OUTPUT, 6 = renderer fail).
- [ ] `docs/plans/README.md` updated with the #2406 row.
- [ ] All three review artifacts (claude, codex, gemini) posted to `scripts/review/results/`.

---

## Adversarial Review Summary

<!-- Filled in after Step 4. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING

Revisions made based on review:
- (none yet)

---

## Risks and Open Questions

- **Risk:** the hang could have a second root cause we haven't identified (e.g. codex checking for a TTY on fd 1 or 2). Mitigation: T26/T27/T28 mock-tests verify argv/stdin shape deterministically; manual live verification in AC list confirms real-world behavior. If hang persists after fix, re-open with trace data (`strace -f -o strace.log`) attached.
- **Risk:** the fix changes the prompt delivery path; it's possible codex's `<stdin>` block framing is subtly different from argv (e.g. extra wrapping). Mitigation: T27 compares the mock's stdin byte-for-byte with the expected prompt. If codex wraps differently, T27 will catch it before it hits production.
- **Risk:** the `-` positional arg is undocumented edge behavior in some codex versions. Mitigation: the help text on the installed CLI confirms `-` support. Pinned by evidence block above.
- **Risk:** if `CODEX_BIN` is an older codex version that doesn't support stdin, fix breaks for that user. Mitigation: script already checks `command -v "$CODEX_BIN"` existence; we additionally recommend documenting the minimum codex version in a brief comment in the script.
- **Risk:** bash `printf '%s' "$prompt_text"` may hit a buffer limit on very long prompts. Mitigation: bash uses heap for variable storage; 5 MB max (already enforced at line 131 by `head -c 5000000`). Pipe writes in chunks from bash builtin's perspective; no documented failure mode below `ARG_MAX`.
- **Open:** should we also add a warning when `CODEX_MAX_PROMPT_CHARS` is exceeded and the compact retry path is chosen? Currently silent. Flag for user — outside the scope of this issue, but trivial follow-up.

---

## Complexity: T2

**T2** — bug fix in a single file with required TDD coverage + a new test fixture. Not T1 because it introduces a new test pattern (argv-vs-stdin assertion) that will be reused for future reviewer-CLI changes; not T3 because there is no architecture change or cross-file design.
