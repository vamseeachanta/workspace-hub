# WRK-1006 Plan — Final Review Confirmation

## Plan Summary

Troubleshoot and harden `scripts/review/submit-to-{claude,codex,gemini}.sh` for reliable
agent-invoked cross-review calls. Deliver a comprehensive test suite (T01–T23) covering
all confirmed failure modes and add CMD env-var injection hooks for testability.

## Key Decisions

- Replace PATH-masking with `CLAUDE_CMD`/`GEMINI_CMD`/`CODEX_BIN` env-var overrides
- DNS failure exits 0 (graceful skip, non-blocking review)
- setsid absence: WARN not exit-1
- CLAUDECODE cleared before subprocess invocation

## Confirmation

confirmed_by: orchestrator-claude
confirmed_at: 2026-03-04T00:00:00Z
decision: passed
