# WRK-1009 Cross-Review — Codex

**Date**: 2026-03-10
**Reviewer**: Codex (gpt-5.4)
**Stage**: 6 — Plan Cross-Review
**Verdict**: APPROVE (with implementation notes)

## Review

*(Derived from plan_codex.md output, session 019cd927)*

### Critical Notes (P2)

**X1 — Retirement rule on missing data** (P2)
The retirement rule as originally written would flag skills with no usage history
(`baseline_usage_rate < 0.05` is trivially true for new skills with 0 usage).
Plan decision ③ correctly specifies SKIP when usage data is absent or stale. This must
be enforced in code: if `calls_in_period` is absent or measurement window is undefined,
result = SKIP, not candidate.

**X2 — Bash YAML parsing fragility** (P2)
Bash grep/awk on YAML is brittle (indentation, multiline values, unicode). The plan
correctly specifies `uv run --no-project python` helpers for all YAML/frontmatter/report
parsing. Shell scripts remain as thin wrappers only.

### Improvement Notes (P3)

**X3 — Atomic writes** (P3)
All state file writes must use temp-file-plus-rename to prevent partial artifacts from
corrupted cron runs. Pattern: write to `<file>.tmp`, then `mv <file>.tmp <file>`.

**X4 — /reflect integration target** (P3)
The repo has documented `/today` section scripts in `scripts/productivity/sections/` but
`/reflect` integration is unclear. Verify the owning renderer before adding hooks.

**X5 — UTC timestamps** (P3)
All JSONL result records and state artifacts must use ISO 8601 UTC timestamps to avoid
midnight-UTC nightly boundary bugs.

**X6 — Test coverage gaps** (P3)
Add test cases for: malformed YAML eval file, malformed SKILL.md frontmatter, stale
usage metadata, normalized duplicate names, missing nightly artifact graceful degradation.

## Summary

| Finding | Severity | Status |
|---------|----------|--------|
| Retirement SKIP on missing data (X1) | P2 | ✓ in plan |
| uv run python for YAML ops (X2) | P2 | ✓ in plan |
| Atomic writes (X3) | P3 | → incorporate |
| /reflect verify (X4) | P3 | → verify Stage 10 |
| UTC timestamps (X5) | P3 | → incorporate |
| Test coverage gaps (X6) | P3 | → expand test strategy |

**APPROVE — P2 items already incorporated. P3 items are Stage 10 reminders.**
