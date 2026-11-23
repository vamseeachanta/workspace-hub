# Plan for #2518: fix(review): harden plan-review fanout provider invocation

> **Status:** plan-approved
> **Complexity:** T2
> **Date:** 2026-04-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2518
> **Review artifacts:** implementation adversarial review to be recorded in closeout; plan-review fanout itself is the affected component and must not be trusted for this bootstrap fix.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/review/plan-review-fanout.sh` — owns provider fan-out for Claude, Codex, and Gemini, writes canonical artifacts under `scripts/review/results/`, and currently degrades non-zero provider exits to `UNAVAILABLE` stubs.
- Found: `scripts/review/tests/test_plan_review_fanout.sh` — existing shell test harness with provider mocks for invocation shape, parallelism, disagreement reporting, and Gemini failure degradation.
- Found: `scripts/review/tests/mocks/{claude,codex,gemini}` — provider mocks that can be extended to simulate stderr-only reviews, empty output, trust-env capture, and timeouts.
- Gap: the wrapper does not treat zero-byte successful outputs as failures, does not promote structured stderr reviews into canonical `.md` artifacts, does not bound provider hangs with per-provider timeouts, and does not explicitly set Gemini workspace-trust env for noninteractive runs.

### Standards
- Not applicable — harness/infrastructure bug, no engineering standard transfer required.

### LLM Wiki pages consulted
- Not applicable — no domain knowledge change.

### Documents consulted
- GitHub issue #2518 — reports post-reboot fanout failures: stalled fanouts, zero-byte/incomplete artifacts, Gemini trust failure, Codex useful content in `.err`, and orphaned provider processes.
- `docs/handoffs/2026-04-27-wave2-wave3-review-status.md` — captures the recovery context that forced `UNAVAILABLE` artifacts and a bounded retry for #2500.
- `scripts/review/plan-review-fanout.sh` — confirms current provider stdout/stderr handling and invocation style.
- `scripts/review/tests/test_plan_review_fanout.sh` — confirms existing coverage and the safe place to add regression tests before implementation.

### Gaps identified
- No regression test for Codex emitting a structured review to stderr while stdout is empty.
- No regression test for successful provider exit with empty stdout/stderr producing a canonical `UNAVAILABLE` artifact.
- No regression test for provider timeout producing an `UNAVAILABLE` artifact rather than hanging indefinitely.
- No regression test for `GEMINI_CLI_TRUST_WORKSPACE=true` on Gemini invocation.

### Evidence (embedded verification)

**Issue status** (verified 2026-04-27T11:35:31-05:00 via `gh issue view`):
- `#2518` — OPEN — `fix(review): harden plan-review fanout provider invocation`; labels: `bug`, `priority:high`, `cat:harness`, `domain:review`.

**File existence** (verified in `/mnt/local-analysis/reconcile-main-20260427`):
- EXISTS: `scripts/review/plan-review-fanout.sh`
- EXISTS: `scripts/review/tests/test_plan_review_fanout.sh`
- EXISTS: `scripts/review/tests/mocks/claude`
- EXISTS: `scripts/review/tests/mocks/codex`
- EXISTS: `scripts/review/tests/mocks/gemini`
- EXISTS: `docs/handoffs/2026-04-27-wave2-wave3-review-status.md`

**Line excerpts checked:**
- `scripts/review/plan-review-fanout.sh` provider invocation block and failure-degradation behavior.
- `scripts/review/tests/test_plan_review_fanout.sh` existing tests for invocation shape, parallel execution, and Gemini failure degradation.

**Gap proofs:**
- Existing tests initially passed 12/12 but did not cover stderr-only review promotion, empty-output normalization, timeout normalization, or Gemini trust env capture.

Minimum source count: 4 distinct sources (#2518 issue body, fanout wrapper, fanout tests, wave2/wave3 recovery handoff).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-27-issue-2518-plan-review-fanout-provider-hardening.md` |
| Implementation | `scripts/review/plan-review-fanout.sh` |
| Tests | `scripts/review/tests/test_plan_review_fanout.sh` |
| Test mocks | `scripts/review/tests/mocks/codex`, `scripts/review/tests/mocks/gemini` |

---

## Deliverable

A hardened `scripts/review/plan-review-fanout.sh` that always produces actionable canonical artifacts for provider failures, empty outputs, stderr-only structured reviews, and timeout/trust failures, with focused shell regression tests.

---

## Pseudocode

```text
function write_unavailable(provider, rc, reason, output_path):
  write standard review artifact sections
  verdict = UNAVAILABLE(provider CLI failed, rc, reason)

function normalize_provider_output(provider, rc, stdout_artifact, stderr_sidecar):
  if stdout empty and stderr has structured review header:
    promote stderr sidecar to canonical artifact
  else if rc != 0:
    write_unavailable(provider, rc, stderr excerpt)
  else if stdout empty:
    write_unavailable(provider, 0, stderr excerpt or empty-provider-output reason)
  remove stderr sidecar

function invoke_provider(provider):
  run provider under timeout -k 5s ${PLAN_REVIEW_PROVIDER_TIMEOUT_SEC:-600}s
  codex: pass combined prompt+plan as argv and close stdin with </dev/null (avoid known `codex exec -` hang path)
  gemini: run from /tmp and set GEMINI_CLI_TRUST_WORKSPACE default true
  normalize_provider_output(provider, rc, out, err)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/review/plan-review-fanout.sh` | add timeout, canonical output normalization, stderr promotion, empty-output handling, Gemini trust env |
| Modify | `scripts/review/tests/test_plan_review_fanout.sh` | add focused regressions and adjust Codex stdin expectation |
| Modify | `scripts/review/tests/mocks/codex` | simulate stderr-only structured review and empty successful output |
| Modify | `scripts/review/tests/mocks/gemini` | capture trust env for assertion |
| Update | `docs/plans/README.md` | index this plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_codex_invocation_inlines_plan_body` | Codex receives inline plan body via argv and closed stdin, not removed flags or `exec -` | fixture plan | capture includes first line and `--- PLAN`, does not use `ARGV: exec -` |
| `test_gemini_invocation_inlines_plan_body` | Gemini invocation includes inline plan body and noninteractive trust env | fixture plan | capture includes `GEMINI_CLI_TRUST_WORKSPACE: true` |
| `test_codex_stderr_review_is_promoted_to_artifact` | structured review emitted on stderr becomes canonical artifact | `MOCK_CODEX_STDERR_REVIEW=1` | `*-codex.md` contains review, no `.err` sidecar |
| `test_empty_provider_output_becomes_unavailable_stub` | zero-byte successful provider output is not silently accepted | `MOCK_CODEX_EMPTY=1` | `*-codex.md` contains `UNAVAILABLE` and `empty provider output` |
| `test_provider_timeout_becomes_unavailable_stub` | provider timeout is bounded and produces `UNAVAILABLE` artifact | short timeout + sleeping mocks | provider artifact contains `UNAVAILABLE` |
| `test_partial_stderr_timeout_becomes_unavailable_stub` | partial structured stderr from a timed-out provider is not promoted as authoritative | short timeout + mock stderr header before sleep | `*-codex.md` contains `UNAVAILABLE`, not partial review |

---

## Acceptance Criteria

- [ ] `bash scripts/review/tests/test_plan_review_fanout.sh` passes.
- [ ] `scripts/review/plan-review-fanout.sh` never leaves zero-byte provider artifacts for known failure/empty-output cases covered by mocks.
- [ ] Structured provider review output on stderr is promoted to the canonical provider `.md` artifact when stdout is empty.
- [ ] Provider hangs are bounded by `PLAN_REVIEW_PROVIDER_TIMEOUT_SEC` and become explicit `UNAVAILABLE` artifacts.
- [ ] Gemini noninteractive runs set `GEMINI_CLI_TRUST_WORKSPACE=true` by default while preserving `/tmp` cwd behavior.
- [ ] Raw `.md.err` sidecars are removed after normalization.
- [ ] Changes are committed and pushed with issue-linked evidence.

---

## Adversarial Review Summary

Plan self-review result: APPROVE for a bootstrap fix because the affected component is the multi-provider plan-review harness itself.

Implementation review artifacts:
- `scripts/review/results/2026-04-27-code-2518-claude.md` / `codex.md` / `gemini.md` — r1 found MAJOR issues: unsafe `codex exec -`, stderr promotion before rc check, partial-timeout coverage gap, cleanup trap gap, and temp-file leak.
- `scripts/review/results/2026-04-27-code-2518-claude-r2.md` / `codex-r2.md` / `gemini-r2.md` — all APPROVE after fixes. Claude listed two non-blocking nits; both were patched by adding shared `error_excerpt()` sanitization and requiring `## Blockers` before stderr promotion.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude r2 | APPROVE | R1 blockers fixed; low residual risk. |
| Codex r2 | APPROVE | No remaining findings. |
| Gemini r2 | APPROVE | No remaining findings. |

**Overall result:** PASS

---

## Risks and Open Questions

- **Risk:** live provider CLIs may have additional environment-specific failure modes not covered by mocks; mitigation is explicit timeout and `UNAVAILABLE` normalization rather than silent success.
- **Risk:** `codex exec -` stdin sentinel must be supported by the installed Codex CLI; verify by targeted real-provider or keep review artifacts explicit if unavailable.
- **Open:** after this issue lands, run a bounded #2500 review retry using the hardened wrapper.

---

## Complexity: T2

**T2** — one shell wrapper plus tests/mocks; non-trivial because it controls cross-provider review artifacts and unattended recovery behavior.
