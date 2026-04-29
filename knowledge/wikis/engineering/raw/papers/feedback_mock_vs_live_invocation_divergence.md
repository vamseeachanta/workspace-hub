> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_mock_vs_live_invocation_divergence.md

---
name: Mock tests can pass while live invocation fails
description: For fixes that depend on external CLI behavior, mocks often accept what reality rejects; always run live repro before declaring done
type: feedback
originSessionId: 6521cd81-8284-4617-9aee-c8a8b0339551
---
For bug fixes that depend on external-CLI behavior (codex, gemini, gh, etc.), **mock-based tests can pass while live invocation fails**. The mock is only as accurate as its author's understanding of the CLI's behavior.

**Why:** Live CLIs have undocumented bugs (e.g. codex v0.121.0 `exec -` + `--output-schema` + `--output-last-message` hangs even with tiny stdin input; discovered in #2406 on 2026-04-20). Mocks replicate the documented contract, so they pass paths that reality rejects.

**How to apply:**
- For any fix that modifies invocations of an external CLI: before declaring the work complete, run a **live repro** against the real CLI with realistic inputs (size, flags, orchestration context).
- Define the live repro as a non-waivable release gate, not a nice-to-have. If the live repro is expensive (quota, time), at least document the exact command so the user can run it once before merging.
- If the live repro fails after mocks pass, treat that as a signal the mock model of the CLI is wrong — investigate the delta, not the test.
- Concrete example #2406 timeline: mock tests passed with stdin+`-` dispatch approach; live repro exposed a codex `-` + schema hang; user-approved inline pivot to `</dev/null` + argv variant; live repro then completed in 2m15s with valid structured output.

**Concrete realization inside #2406:** the approved v3 plan was based on the hypothesis that argv-size was the root cause. Live repro revealed stdin-inheritance was the real cause and that the planned `-` sentinel approach had its own separate codex bug. A mid-session plan deviation (user-approved) pivoted to the minimal `</dev/null` fix that actually works against real codex.
