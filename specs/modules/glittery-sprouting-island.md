# WRK-1111 Plan: @ File Reference Pipeline

## Context

Claude Code's `@file` syntax in CLAUDE.md causes a file's contents to be auto-included
in every session context — eliminating the recurring search-and-read cycle for stable,
high-value references. Resource intelligence (Stage 2) identified 3 approved candidates
from the original 6; others were rejected for size (>200 lines) or not found.

## Approved Candidates

| File | Lines | Changes/6mo | Placement |
|------|-------|-------------|-----------|
| `config/deps/cross-repo-graph.yaml` | 38 | 1 | workspace-hub CLAUDE.md |
| `config/onboarding/repo-map.yaml` | 60 | 1 | workspace-hub CLAUDE.md |
| `worldenergydata/src/worldenergydata/modules/__init__.py` | 37 | 1 | worldenergydata AGENTS.md |

worldenergydata CLAUDE.md is at 19/20 lines → references overflow to AGENTS.md (7 lines headroom).

## Implementation Steps

### Step 1 — TDD: line-count validation script

Write `scripts/work-queue/check-claude-md-limits.sh` before any edits:
- Reads list of agent harness files (CLAUDE.md, AGENTS.md, CODEX.md, GEMINI.md)
- Checks line count ≤ 20 for each
- Exits 1 if any file exceeds limit; prints offenders

Run the script **before** edits to confirm baseline, then **after** each file edit to confirm
the 20-line limit is not breached.

### Step 2 — Edit workspace-hub/CLAUDE.md

Current line count: 17. Headroom: 3 lines.

Add one line to the `## Quick Reference` section:

```
- Dep graph: @config/deps/cross-repo-graph.yaml | Repo map: @config/onboarding/repo-map.yaml
```

Result: 18 lines (within limit).

File: `/mnt/local-analysis/workspace-hub/CLAUDE.md`

### Step 3 — Edit worldenergydata/AGENTS.md

Current line count: 13. Headroom: 7 lines.

Append a `## Key References` section:

```markdown
## Key References
Module compat shim: @src/worldenergydata/modules/__init__.py — check before changing module exports
```

Result: 16 lines (within limit).

File: `/mnt/local-analysis/workspace-hub/worldenergydata/AGENTS.md`

### Step 4 — Write docs/context-pipeline.md

Create `/mnt/local-analysis/workspace-hub/docs/context-pipeline.md` documenting:
- What `@file` syntax does and why it was adopted
- Candidate evaluation criteria (≤200 lines, ≤2 changes/month)
- Audit table (all 6 candidates, decisions + rationale)
- Maintenance guide: how to add/remove @ references in future

### Step 5 — Run validation

```bash
bash scripts/work-queue/check-claude-md-limits.sh   # all files ≤20 lines
grep -n "@" CLAUDE.md worldenergydata/AGENTS.md     # confirm @ syntax present
```

## Files to Modify

| File | Change |
|------|--------|
| `CLAUDE.md` | +1 line to Quick Reference |
| `worldenergydata/AGENTS.md` | +3 lines Key References section |

## Files to Create

| File | Purpose |
|------|---------|
| `scripts/work-queue/check-claude-md-limits.sh` | TDD guard — line limit enforcer |
| `docs/context-pipeline.md` | AC artifact — documents @ reference decisions |

## Verification

1. `bash scripts/work-queue/check-claude-md-limits.sh` exits 0
2. `grep '@' CLAUDE.md` shows both hub references
3. `grep '@' worldenergydata/AGENTS.md` shows worldenergydata reference
4. `wc -l CLAUDE.md` → ≤20
5. `wc -l worldenergydata/AGENTS.md` → ≤20

## Non-goals

- Repos where no stable, small candidate was found (assethold, assetutilities, digitalmodel)
- @ references for files >200 lines or with high churn
