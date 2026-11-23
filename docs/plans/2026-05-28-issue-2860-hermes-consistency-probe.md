# Plan for #2860: per-machine Hermes consistency probe

> **Status:** plan-review · **Complexity:** T1 · **Date:** 2026-05-28 · **Client:** N/A
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2860

## Resource Intelligence
- `config/agents/hermes/SOUL.runtime.md` (canonical identity), `scripts/agents/build-soul-runtime.sh` + `install-soul-runtime.sh` (drift/symlink), `config/scheduled-tasks/schedule-tasks.yaml` (bridges #2846), `feedback_hermes_no_openrouter_always_gpt55` (routing policy). Gap: no per-machine Hermes verifier exists; `scripts/readiness/` has nightly-readiness.sh + telegram_hermes_readiness.py but nothing probing Hermes config consistency.

## Deliverable
`scripts/readiness/hermes-consistency-check.sh` — read-only probe (PASS/WARN/FAIL, exit 1 on FAIL) of harness/memory/routing/skills/auth/bridges, runnable under Git Bash on Windows (for ace-win-1). Plus the session handoff doc.

## Files
| Action | Path |
|---|---|
| Create | scripts/readiness/hermes-consistency-check.sh |
| Create | docs/session-handoffs/2026-05-28-orchestrator-consistency-handoff.md |
| Create | docs/plans/2026-05-28-issue-2860-hermes-consistency-probe.md |

## Adversarial self-review (T1)
- **Read-only:** no mutations except `git fetch` (remote-tracking refs only) for the behind-count — acceptable for a probe; documented.
- **No secret leakage:** checks key NAMES, never prints values.
- **False-positive fix:** routing greps now strip comment lines (`grep -vE '^\s*#'`) so a "# openrouter removed" note doesn't false-FAIL (caught in smoke-run on ace-linux-1).
- **Portability:** Git-Bash-safe (`hostname -s` fallback, `readlink`/`diff` present); ANSI colors via printf.
- **Self-consistency:** no hardcoded abs paths (uses `$HOME`/repo-root detection) — passes check-no-abs-paths.

## Acceptance
- [ ] `bash -n` clean; smoke-run yields sensible PASS/WARN/FAIL.
- [ ] No secret values printed; no mutations beyond `git fetch`.
- [ ] Committed to main + handoff doc landed.

## Cross-review
T1 → single-author + inline adversarial self-review (cross-provider Codex/Gemini dispatch unavailable from Claude-Code session; documented per `feedback_permission_gate_blocks_cross_review`).
