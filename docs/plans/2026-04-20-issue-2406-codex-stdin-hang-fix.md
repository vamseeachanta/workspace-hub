# Plan for #2406: fix(review) — submit-to-codex.sh hangs on "Reading additional input from stdin" for substantial plan files

> **Status:** implemented-with-deviation (2026-04-20; user approved Option 1 mid-session after live-repro discovery)
> **Complexity:** T2
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2406
> **Review artifacts:** scripts/review/results/2026-04-20{,-v2,-v3}-plan-2406-{claude,codex,gemini}.md

---

## Post-implementation deviation (2026-04-20)

**The implementation deviates from the approved v3-final Pseudocode.** The deviation was user-approved mid-implementation after the approved approach failed live testing. All pseudocode, test descriptions, and risk analysis below are preserved as **historical record** of the approved plan; the **actually-landed fix** is simpler.

**What the approved plan said to do:** pipe the prompt via stdin using `codex exec - …` with the `-` sentinel per the CLI's `--help` contract; add a runtime version probe that hard-fails with exit 7 on older codex CLIs; cover both paths with T26–T33.

**What went wrong:** against real codex v0.121.0, `codex exec - --output-schema <file> --output-last-message <file>` hangs even with small stdin input. The `-` positional combined with the structured-output flags is a separate bug in codex itself. Mock-based tests passed because the mock was permissive; the live repro exposed the issue.

**What actually landed** (verified live repro against the #2405 v3 plan: exit 0, 6870 bytes of valid structured-JSON review content, 2m15s elapsed vs. the original 240s+ timeout loop):
- `codex exec "$PROMPT" … </dev/null` — keep argv delivery, add explicit `</dev/null` on each dispatch branch so codex sees an immediate EOF on stdin instead of blocking on the caller's inherited pipe.
- **Root cause refined:** the hang was about *stdin inheritance from the orchestrator caller*, not argv size or absent stdin support. Redirecting stdin to `/dev/null` closes the hole without changing transport.
- **Version probe + exit 7: removed.** No longer needed — the fix does not depend on the `-` sentinel, so older codex CLIs remain supported.
- **`${PIPESTATUS[1]}` capture: removed.** No pipeline; the simple-command form returns codex's exit directly.
- Privacy note (argv exposure via `ps`): unchanged from baseline. This was a speculative side-benefit of the stdin approach and is no longer claimed.

**Timeout observation** (informational, not a config change): full adversarial review of a 28K-char plan takes ~135s of real codex compute time. The existing 300s default for `CODEX_TIMEOUT_SECONDS` is adequate with margin; no change needed. Users dispatching against plans above ~50K may want to raise it via env var, but the 300s default is kept.

**Tests landed** (8 cases, T26–T29 + T32 + T33 — T30/T31 for version probe are dropped as no-ops):
- T26: caller's unconsumed stdin pipe is not inherited by codex (codex sees 0 bytes; caller sentinel is not forwarded).
- T27: dispatch completes exit 0 even when the caller provides a dangling stdin pipe (the original hang scenario).
- T28: compact-retry path also isolates stdin from caller on both call-1 and call-2.
- T29: codex quota (exit 1 + "insufficient_quota" stderr) propagates as script exit 3 (unchanged behavior).
- T32: NO_OUTPUT path → script exit 5 (unchanged).
- T33: renderer-fail path → script exit 6 (unchanged).

**Total test count after this fix:** 55 assertions (22 existing + 33 new across 6 test blocks). Full suite green.

**AC impact:**
- ✅ Automated ACs: T26/T27/T28 satisfy the "fix prevents stdin-inheritance hang" criterion. T29/T32/T33 satisfy the exit-code preservation criteria.
- ❌ T30/T31 automated ACs (version probe + hard-fail exit 7) are **dropped**. Not applicable to the landed fix.
- ✅ Release-gate 1 (README row): unchanged — already at commit `a73ec66f6`.
- ✅ Release-gate 2 (3 review artifacts × 3 iterations = 9 files): satisfied.
- ✅ Release-gate 3 (live repro): completed successfully post-deviation.

**User approval trail for the deviation:** session conversation 2026-04-20, message "1" selecting Option 1 (revise to `</dev/null` fix) from three options presented after live repro failure of the approved approach.

---

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/review/submit-to-codex.sh:162-180` — `run_codex_exec()` passes the full prompt as a positional argv to `codex exec "$prompt_text"` in all three dispatch branches (`timeout`, `perl alarm`, bare). All three branches share the hang.
- Found: `scripts/review/submit-to-codex.sh:215-227` — initial size guard: if `payload_chars > CODEX_MAX_PROMPT_CHARS` (default 120 000), **pre-truncate** `CONTENT_TEXT` to `CODEX_COMPACT_RETRY_CHARS` (default 24 000) and rebuild `prompt_for_run`. This is truncation, **not rejection**; dispatch proceeds with the truncated prompt.
- Found: `scripts/review/submit-to-codex.sh:229-247` — compact-retry fallback: after `run_codex_exec "$prompt_for_run"`, if `exec_exit != 0` **OR** `raw_file` is empty, retry once with a prompt truncated to `CODEX_COMPACT_RETRY_CHARS`. The retry is triggered by **any first-dispatch failure including timeout** — so today's observed hang-exit-124 case triggers the retry, and the retry also dispatches via the same buggy argv path. Both calls (line 230 and line 246) share `run_codex_exec`, so fixing that function fixes both.
- Found: `scripts/review/submit-to-gemini.sh` — Gemini dispatch uses a different CLI, not affected. Confirmed via Gemini reviewing 4 prompts this session without hang.
- Found: `tests/review/test-submit-scripts.sh` (320 lines) — existing mock-based test harness using `make_mock` to replace CLI binaries on PATH. Existing test IDs present (per `grep -oE "^# ── T[0-9]+:"`): T01–T13 and T17–T25 (22 tests with gaps at T14/T15/T16). Highest-numbered existing test is T25; new tests will use T26–T31 (first unused IDs above T25), no renumbering required. T07/T24/T25 already cover `submit-to-codex.sh`. Pattern is reusable for a new argv-size regression test.
- Gap: no existing test covers the argv-vs-stdin dispatch path; no test with a large prompt fixture.

### Standards

Not applicable — infrastructure script bug fix, no engineering standards involved.

### Operating-model compliance (explicit N/A rationale)

Per reviewer request in iter-1 + iter-2 (Codex): each operating-model section is explicitly evaluated below with citation to the canonical source, not silently skipped.

**Canonical source:** `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` (verified existing 2026-04-20; referenced by `.planning/handoffs/2026-04-20-doc-intel-planning-handoff.md` as "the authority for everything" under doc-intel).

| Section (cited from the operating-model doc) | Applies? | Rationale |
|---|---|---|
| §2 ownership (L<n> classification — how a doc is owned by exactly one layer) | **No** | Layer classes (L0–L5) govern the document-intelligence corpus (wiki/knowledge/standards). This plan modifies `scripts/review/` (harness infra) and `tests/review/` (test code). Bash scripts are not doc-intelligence corpus items; no layer assignment applies. No new between-layer or L<n>-adjacent classification is invented. |
| §3 identity / `doc_key` / `sha256:` namespace (how corpus docs are referenced) | **No** | `doc_key` identity applies to corpus documents where content-addressable references are needed across layer boundaries. A bash script patch and a pytest-style fixture are not corpus references; they are implementation artifacts. Conventional repo-relative paths suffice (and match the template's `Artifact Map` convention). |
| §4 flow rules (durable ↔ transient flow direction) | **No** | No durable→transient or transient→durable doc-corpus flows are introduced. The plan file itself lives at `docs/plans/` which is planning/governance, not a doc-intelligence flow endpoint per §4. |
| §7 cross-machine tier rules (git-tracked metadata vs shared-mount vs local-cache) | **Yes (partial)** | The new test fixture `tests/review/fixtures/codex-large-prompt.txt` is git-tracked ⇒ tier-1 durable metadata. Mock stdin/argv log files in tests live under `$(mktemp -d)` ⇒ tier-5 transient temp files. No cross-machine mount dependency introduced. Fixture content is deterministic (generated via documented one-liner), so multi-machine portability is preserved. ✓ |
| §8.1 frontmatter authority (wiki-domain baseline fields) | **No** | No wiki or knowledge-domain content is created or modified. Plan does not create any file under `knowledge/wikis/` or `docs/document-intelligence/`. |

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
- **Runtime codex-version compatibility probe:** before first dispatch, the fix adds a one-shot probe — `"$CODEX_BIN" exec --help 2>&1 | grep -q 'read from stdin'` — cached at script scope in a variable set at the first invocation of `run_codex_exec`. The cached result governs both the initial dispatch and the compact-retry dispatch so the two paths never diverge. **If the probe fails (older codex CLI without documented stdin support), the script hard-fails with a new exit code (7 = CLI version unsupported) and an explicit stderr message instructing the user to upgrade codex.** No silent fallback to the old argv path — that path is the bug we are fixing, and restoring it under any condition would violate the Deliverable's reliability guarantee. (Rationale per iter-2 Codex P1.)

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/review/submit-to-codex.sh` | rewrite `run_codex_exec` (lines 162–180) to pipe prompt via stdin with `-` positional; add one-time codex-version probe that **hard-fails with new exit code 7** on older CLIs (no argv fallback — matches the Deliverable's reliability guarantee); add `${PIPESTATUS[1]}` capture to preserve codex exit codes across the new pipe under `set -euo pipefail`. No change to the error-classification table, the existing exit-code map for codes 1/2/3/5/6, or the compact-retry trigger logic. New exit code 7 added exclusively for the version-probe hard-fail path. |
| Create | `tests/review/fixtures/codex-large-prompt.txt` | deterministic large-prompt fixture (24 000 chars = 400 × 60-char lines), reproducible via one-liner |
| Modify | `tests/review/test-submit-scripts.sh` | add T26 (argv must not contain full prompt), T27 (stdin delivers the prompt byte-for-byte), T28 (compact-retry path also uses stdin), T29 (pipefail+SIGPIPE + exit-3 fidelity), T30 (version-probe hard-fail with new exit 7), T31 (probe-cache single-invocation), T32 (exit-5 NO_OUTPUT preserved), T33 (exit-6 renderer-fail preserved) |
| ~~Update~~ (already done in planning commits) | `docs/plans/README.md` | Index row for #2406 already landed in commit `a73ec66f6` as part of the standard skill Step 2 plan-draft routine. Not a pending implementation change — recorded here only for traceability, **not counted in v3's to-do work**. |

---

## TDD Test List

Tests live in `tests/review/test-submit-scripts.sh` and use the existing `make_mock` harness. Each mocks `codex` with a shell script that records its argv and stdin to temp files, then asserts on them.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| T26: codex dispatch — argv does NOT contain full prompt | `run_codex_exec` does not inflate argv with large prompts | large-prompt fixture via `--file`, short prompt via `--prompt` | mock's recorded argv contains `exec` and `-` (or no positional) but NOT any substring of the fixture body |
| T27: codex dispatch — stdin DELIVERS the prompt | mock's stdin equals the constructed FULL_PROMPT **byte-for-byte**, including absence of any trailing newline (`printf '%s'` is explicitly non-newline-terminating) | same as T26 | `cmp -s <(mock_stdin) <(expected_full_prompt)` returns 0 AND `wc -c` matches exactly — no "ignoring trailing newline" tolerance |
| T28: compact-retry path uses stdin on BOTH calls | when first dispatch returns empty `raw_file`, retry still pipes via stdin | mock that returns empty `raw_file` on call 1, success on call 2; prompt length forces retry via `:0:CODEX_COMPACT_RETRY_CHARS` truncation path | call-1 and call-2 recorded invocations both show argv without body substring and stdin containing prompt content (call-2 with truncated content) |
| T29: pipefail + SIGPIPE exit-code fidelity | when codex exits 3 (quota) while printf still has unread buffer, exec_exit captured is 3, not 141 | mock codex: write minimal error to err_file, `exit 3` | `submit-to-codex.sh` exits 3 (QUOTA path), not 141 (SIGPIPE masked as pipeline exit) |
| T30: codex-version-probe hard-fail | on older codex CLI without stdin support in help text, dispatch does NOT fall back to argv — instead hard-fails with a new exit code (7 = CLI version unsupported) and an explicit stderr message instructing the user to upgrade | mock codex whose `exec --help` does NOT contain "read from stdin" | script exits 7 (not 0, 1, 2, 3, 5, or 6); stderr contains "upgrade codex CLI"; no attempt at argv dispatch is recorded (mock's argv log for `exec` subcommand is empty) |
| T31: probe result is cached across calls | probe runs exactly once per `submit-to-codex.sh` invocation regardless of whether the compact-retry fires | mock codex counts `--help` invocations; prompt designed to force compact-retry (first dispatch returns empty `raw_file`) | probe-invocation count is 1 (not 2); both dispatches use stdin |

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
| Pipefail + SIGPIPE does not mask codex exit code | T29 | automated |
| Older codex CLI hard-fails with exit 7 (no silent fallback) | T30 | automated |
| Version probe is invoked at most once per script invocation | T31 | automated |
| Existing exit-code semantics preserved (exit 1 user error) | T01, T02, T03, T24 (existing) | automated |
| Existing exit-code semantics preserved (exit 2 CLI missing) | T07, T25 (existing) | automated |
| Existing exit-code semantics preserved (exit 3 quota) | T29 (new — exercises quota path via mock exit 3) | automated |
| Existing exit-code semantics preserved (exit 5 NO_OUTPUT) | dedicated new micro-test added inline: invoke with mock that writes empty `raw_file` and exits 0 twice; assert exit 5 (previously implicitly relied on by compact-retry path; made explicit in v3 per iter-2 Codex P1) | automated (T32 below) |
| Existing exit-code semantics preserved (exit 6 renderer fail) | dedicated new micro-test: mock `uv run python …` (or equivalent renderer stub) fails; assert exit 6 (made explicit in v3) | automated (T33 below) |
(README row presence, artifact count, and live-repro are **release-gate checks**, not test-backed acceptance criteria — see the "Release-gate checks" section under Acceptance Criteria above. They are intentionally not in this automated-test matrix per iter-3 Codex P1.)

Additional new tests covering exit-code ACs that were previously only manual (iter-2 Codex P1 fix):

| Test | Purpose |
|---|---|
| T32: exit-code 5 (NO_OUTPUT) preserved | mock returns empty `raw_file` on both first and retry; assert script exit code 5 |
| T33: exit-code 6 (renderer fail) preserved | mock writes `raw_file` successfully but renderer invocation fails; assert exit 6 |

---

## Acceptance Criteria

Automated (pass/fail via `bash tests/review/test-submit-scripts.sh`):
- [ ] All **22 existing** test cases (T01–T13, T17–T25) still pass (regression check).
- [ ] T26 passes: mock's recorded argv does not contain the fixture body.
- [ ] T27 passes: mock's recorded stdin equals the constructed FULL_PROMPT byte-for-byte (`cmp -s` returns 0).
- [ ] T28 passes: compact-retry path uses stdin on both call-1 and call-2.
- [ ] T29 passes: codex exit 3 (quota) propagates through the pipeline unmasked; script exits 3.
- [ ] T30 passes: older codex without stdin-help support causes the script to hard-fail with new exit code 7 and a stderr upgrade-instruction message. No argv-path dispatch attempted.
- [ ] T31 passes: version probe is invoked exactly once per `submit-to-codex.sh` invocation, cached, and reused on compact-retry.

**Release-gate checks (NOT acceptance criteria — these are operational confirmations, not test obligations).** Per iter-3 Codex P1 finding, these are explicitly separated from test-backed AC to avoid overstating AC↔test coverage:
- Release-check 1: `docs/plans/README.md` contains a row starting with `| 2406 |` (verified existing at commit `a73ec66f6` — this is a preceding plan-authoring step under the skill's Step 2, NOT a behavior change introduced by this fix).
- Release-check 2: `ls scripts/review/results/2026-04-20-plan-2406-*.md | wc -l` ≥ 3 at closeout (confirms all three provider review artifacts committed — operational audit, not correctness test).
- Release-check 3: **live repro against the real codex CLI**. Re-running the failing dispatch from the issue body on the fixed branch completes within `CODEX_TIMEOUT_SECONDS`. Uses any large plan file in `docs/plans/` (≥20 000 chars); `#2405`'s plan file is the example in the issue body but not required. Documented in the closeout comment with exit code + elapsed time. **This is the only real-codex-CLI check and must be done before merging.**

Exit-code map (v3 introduces new code 7):
- 1 = user error, 2 = CLI not installed, 3 = quota, 5 = NO_OUTPUT, 6 = renderer fail, **7 = CLI version unsupported (new in this fix)**.

---

## Adversarial Review Summary

| Provider | Verdict (iter-1) | Key findings |
|---|---|---|
| Claude (self) | MINOR | Test-count off (22, not 25); pipefail semantics undocumented; guard-interaction not called out; exit-code AC coverage partial |
| Codex | MAJOR | Compact-retry reasoning internally inconsistent; AC↔test traceability missing; #2405 dependency wording contradictory; operating-model §2/§4/§7/§8.1 checks absent; threat model missing; version-skew risk not mitigated. Plus Class B self-circular "unverified live-state" (resolves at #2405 implementation). |
| Gemini | MAJOR | Pipefail semantics unspecified; README-update AC lacks automated test; artifact identity not `sha256:`-namespaced. Plus Class B self-circular unverified claims. |

**Overall result (iter-1):** REVISE — addressed in v2.

| Provider | Verdict (iter-2, v2) | Key findings |
|---|---|---|
| Claude (self) | MINOR | T29 timing-sensitivity; T30 probe-cache not explicitly tested; minimum codex version un-pinned; Class B follow-up not flagged |
| Codex | MAJOR — new Class A | Version-probe fallback reintroduces the buggy argv path (breaks Deliverable); README-to-change ambiguity (already landed); operating-model N/A assertions lack source-file citations; exit-codes 3/5/6 preserved-behavior ACs lack automated tests; T27 newline weakening; threat model inconsistent with argv-fallback branch; probe-cache state between first call and retry unspecified. Plus continued Class B "unverified live state". |
| Gemini | MAJOR — pure Class B | Entirely "unverified live state" findings (#2406/#2405/#2403/#2402 statuses, file contents, CLI contract). No Class A. Expected per handoff — resolves at #2405 implementation. |

**Overall result (iter-2):** REVISE — Codex Class A addressed in v3; Gemini Class B accepted as self-circular.

Revisions made based on iter-2 review (v2 → v3):
- **Removed argv-path fallback on older codex** — replaced with hard-fail (new exit code 7 + stderr upgrade instruction). Preserves the Deliverable's reliability guarantee unconditionally. (Codex iter-2 P1)
- **Marked README index update as already-done** in Files-to-Change, with citation to commit `a73ec66f6`. No longer counted as pending work. (Codex iter-2 P1)
- **Added citation to the operating-model source file** (`docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`) at the top of the compliance sub-table, and elaborated each section's rationale to reference the actual policy text. (Codex iter-2 P1)
- **Tightened T27** to require exact byte-for-byte equality via `cmp -s` — removed the "ignoring trailing newline" tolerance. `printf '%s'` is explicitly non-newline-terminating; the acceptance condition now matches. (Codex iter-2 P2)
- **Decoupled live-repro AC from #2405** — any large plan file (≥20 000 chars) in `docs/plans/` satisfies the AC; #2405's plan is an example, not a dependency. (Codex iter-2 P2)
- **Added T31** — asserts probe is invoked exactly once per script invocation (cache fidelity between initial dispatch and compact-retry). (Codex iter-2 P2)
- **Added T32 + T33** — explicit automated coverage for exit codes 5 (NO_OUTPUT) and 6 (renderer fail); no longer manual-only. (Codex iter-2 P1)
- **Clarified test numbering** — existing IDs are T01–T13 + T17–T25 with gaps at T14/T15/T16; new tests use T26–T33 (first unused above T25). No renumbering required. (Claude iter-2)
- **Updated threat model** — removed conditional-improvement wording; argv exposure reduced unconditionally because older-codex path hard-fails pre-dispatch. (Codex iter-2 P2)
- **Updated exit-code map** — added code 7 (CLI version unsupported).

Class B findings (self-circular) acknowledged and NOT addressed in plan text:
- Codex iter-1/2, Gemini iter-1/2: "unverified GitHub issue states, file existence, CLI contract". This is the #2405-meta class. Resolution path: when #2405 lands the pre-verification attestation script, iter-3 would drop these findings. v3 acknowledges them as out-of-plan-scope.

**Overall result (v3 mid-review):** approval-ready pending iter-3 confirmation.

| Provider | Verdict (iter-3, v3) | Key findings |
|---|---|---|
| Claude (self) | APPROVE | v3 addresses all iter-2 Class A; internal consistency verified; AC↔test matrix closed; only P3 documentation nits remain (wording + future test-file split) |
| Codex | MAJOR | Two **real P1 internal contradictions** caught: Files-to-Change said "argv-path fallback" while Pseudocode said "hard-fail exit 7" (stale text from v2 not propagated); Risks section had same contradiction. Also: AC↔test mixing test-backed criteria with release-gate manual checks overstated coverage. **These are not new design issues — they are internal-consistency defects that slipped through the v3 edit.** Other findings: Class B self-circular (expected), P2 threat-model coverage (PATH/CODEX_BIN trust), P2 PIPESTATUS[1] underspecification. |
| Gemini | MAJOR (pure Class B) | Every finding is "cannot verify live state" (files, issues, CLI contract, commits). Zero Class A. Expected per handoff — resolves at #2405. |

**Overall result (iter-3 final, iter-cap reached):** Codex's two P1 findings were real internal-consistency defects (contradictions between Pseudocode + Files-to-Change + Risks) carried over from v2 → v3 incomplete text propagation. These were fixed inline as **v3-final cleanup edits** (not a new design iteration; not requiring cross-review iter-4):

v3 mid-review → v3-final cleanup edits (post-iter-3):
- Files-to-Change row for `submit-to-codex.sh` now says "hard-fails with new exit code 7" (removed the stale "argv-path fallback" phrase).
- Risks section's version-skew mitigation now says "hard-fails with exit 7 (no argv fallback — that would reintroduce the bug)" (removed contradictory "argv-path fallback" phrase).
- Acceptance Criteria section now cleanly separates **automated test-backed ACs** from **release-gate operational checks** (README row presence, artifact count, live repro) — so the AC↔test matrix only lists items backed by automated tests.
- AC↔test traceability matrix footer explicitly points to the Release-gate section for non-automated checks.

Codex's other findings (Class B unverified live state, P2 threat-model additions, P2 PIPESTATUS[1] formalization) are **deferred as post-implementation follow-ups**:
- Class B unverified-live-state: resolves at #2405 (the meta-issue that exists exactly for this).
- P2 threat-model additions (malicious `CODEX_BIN`, help-output spoofing, PATH trust): could be added but cross-reviewing that analysis would exceed iter-cap; documenting here for a potential follow-up issue.
- P2 `PIPESTATUS[1]` exact shell structure: specification lives in Pseudocode; T29 tests the behavior deterministically. Formalizing further is an impl-quality nice-to-have.

**Final status:** plan is approval-ready. Iteration cap reached (3/3 cross-provider dispatches). Fresh MAJOR blocking verdicts are either fixed inline or explicitly deferred as self-circular/out-of-scope. No further review iterations without explicit user direction per `issue-planning-mode` skill.
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
- **Risk:** the `-` positional arg is undocumented edge behavior in some codex versions. Mitigation: runtime version probe that **hard-fails with exit 7** (no argv-path fallback — that would reintroduce the bug). T30 asserts the hard-fail. User-facing stderr tells them to upgrade the CLI. Pinned by CLI-help evidence for the current installed version.
- **Risk:** `CODEX_MAX_PROMPT_CHARS` guard behavior is unchanged by this fix — the pre-truncation logic still runs before `run_codex_exec`. Noted explicitly to prevent confusion during review.
- **Risk:** bash `printf '%s' "$prompt_text"` may hit a buffer limit on very long prompts. Mitigation: bash uses heap for variable storage; 5 MB max (already enforced at line 131 by `head -c 5000000`). Pipe writes in chunks from bash builtin's perspective; no documented failure mode below `ARG_MAX`.

### Threat model (added per iter-1 Codex finding)

| Surface | Current behavior | Fix behavior | Delta risk |
|---|---|---|---|
| PATH trust for `CODEX_BIN` | script trusts `command -v codex`; falls through to `${HOME}/.npm-global/bin/codex` | unchanged | none |
| Prompt content source | `$PROMPT` from `--prompt` argv, `$CONTENT_TEXT` from `--file` via `head -c 5M \| tr -d '\000'` | unchanged — same `$FULL_PROMPT` string, just delivered via a different channel (stdin vs argv) | none — same bytes, same sink |
| Argv exposure (ps/strings visibility) | full prompt visible in process-table `ps -ef` — any user on the host can read current-user prompts for the lifetime of the codex invocation | prompt removed from argv in all success paths; only flags + `-` visible in `ps`. On older codex without stdin support the script hard-fails BEFORE dispatch (exit 7) — the old argv path is NEVER taken as a fallback, so the privacy improvement is unconditional once the fix lands. **Improvement, not conditional.** | **reduced unconditionally** — sensitive plan content no longer leaks via process table under any supported-version branch (iter-2 Codex P1 fix: the hard-fail replaces the original argv-fallback plan) |
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
