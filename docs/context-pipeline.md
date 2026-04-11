# @ File Reference Pipeline

> Decision log and maintenance guide for `@file` references in agent harness files.

## What `@file` syntax does

Claude Code's `@file` mention in `CLAUDE.md` (or `AGENTS.md`, `CODEX.md`, `GEMINI.md`)
causes that file's contents to be auto-included in every session context window.
Effect: the agent can answer questions about the referenced file immediately, without a
manual search-and-read round-trip.

Adopted from course learning (WRK-1111): `@prisma/schema.prisma` in CLAUDE.md eliminates
the recurring cost of pointing the agent at schemas, dep maps, and config files that are
relevant to nearly every request.

## Evaluation Criteria

A file is approved for `@` reference only if **all** of the following hold:

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| File size | ≤ 200 lines | Larger files bloat every request |
| Churn rate | ≤ 2 changes / month (≈ ≤1 change / 6 months observed) | High-churn refs go stale and mislead |
| Always-relevant | Referenced in ≥50% of sessions | Low-relevance refs waste token budget |
| Harness headroom | Target file stays ≤ 20 lines after edit | Hard rule per `coding-style.md` |

## Candidate Audit (WRK-1111, 2026-03-12)

| File | Lines | Changes/6mo | Decision | Placement | Rationale |
|------|-------|-------------|----------|-----------|-----------|
| `config/deps/cross-repo-graph.yaml` | 38 | 1 | **APPROVED** | workspace-hub CLAUDE.md | Dep routing for every cross-repo decision |
| `config/onboarding/repo-map.yaml` | 60 | 1 | **APPROVED** | workspace-hub CLAUDE.md | Repo capability map used in every session-start |
| `worldenergydata/src/worldenergydata/modules/__init__.py` | 37 | 1 | **APPROVED** | worldenergydata AGENTS.md | Backward-compat shim — preserve before changing exports |
| `.claude/skills/workspace-hub/workstations/SKILL.md` | >200 | unknown | **REJECTED** | — | Exceeds 200-line size limit |
| `assethold/prisma/schema.prisma` | unknown | unknown | **REJECTED** | — | File not found in repo |
| `digitalmodel/src/geometry/circle.py` | unknown | unknown | **REJECTED** | — | File not found in repo |

Note: worldenergydata CLAUDE.md was at 19/20 lines → references overflow to AGENTS.md (7 lines headroom).

## Current `@` References

### workspace-hub `CLAUDE.md`
```
- Dep graph: @config/deps/cross-repo-graph.yaml | Repo map: @config/onboarding/repo-map.yaml
```

### worldenergydata `AGENTS.md`
```
## Key References
Module compat shim: @src/worldenergydata/modules/__init__.py — check before changing module exports
```

## Maintenance Guide

### Adding a new `@` reference

1. Confirm all 4 evaluation criteria above are met.
2. Run `uv run --no-project python scripts/quality/check_config_drift.py --repo workspace-hub` before and after editing to verify harness-file limits still pass.
3. If the target harness file is within 2 lines of 20, overflow to `AGENTS.md` instead.
4. Document the decision in the **Candidate Audit** table above.
5. Commit with `chore(context): add @ reference for <file>`.

### Removing an `@` reference

When a referenced file exceeds the size/churn thresholds or is no longer always-relevant:

1. Remove the `@file` line from the harness file.
2. Mark the row `RETIRED` in the Candidate Audit table with date.
3. Commit with `chore(context): retire @ reference for <file>`.

### Periodic review

Review this table whenever a referenced file grows beyond 200 lines or receives its third
change in a 6-month window. Use `git log --follow -p <file>` to check churn.

## Related

- `scripts/quality/check_config_drift.py --repo workspace-hub` — current harness drift/line-limit check
- `.claude/rules/coding-style.md §Agent Harness Files` — hard limit policy
- WRK-1111 — implementation WRK for this pipeline
