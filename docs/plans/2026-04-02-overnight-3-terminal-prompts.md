# Overnight 3-Terminal Batch — Cross-Agent Session Corpus Audit

**Date**: 2026-04-02
**Issue**: #1720
**Machine**: ace-linux-1
**Type**: Analysis-only (read-only, no code modifications)

## Terminal Allocation

| Terminal | Agent | Phases | Workload |
|----------|-------|--------|----------|
| T1 | Claude Code | A (baseline) + B (skill gaps) | 153K+ Claude JSONL + 691 skills scan |
| T2 | Hermes | C (dead skills) + D (corrections) + F (memory) | 547 scored skills + 8,965 corrections + 24 repos |
| T3 | Codex | E (routing intel) + G (repo audit) | All 4 agents' logs + 24 repo ecosystem |

## Git Contention Map

```
Terminal 1 writes: analysis/cross-agent-audit-20260402/phase-a-*
                   analysis/cross-agent-audit-20260402/phase-b-*
Terminal 2 writes: analysis/cross-agent-audit-20260402/phase-c-*
                   analysis/cross-agent-audit-20260402/phase-d-*
                   analysis/cross-agent-audit-20260402/phase-f-*
Terminal 3 writes: analysis/cross-agent-audit-20260402/phase-e-*
                   analysis/cross-agent-audit-20260402/phase-g-*
Zero overlap.
```

## Issue-to-Terminal Mapping

| Issue | Phase | Terminal |
|------:|-------|----------|
| #1720 | Phase A: Cross-agent baseline | T1 (Claude) |
| #1720 | Phase B: Skill gap detection | T1 (Claude) |
| #1720 | Phase C: Dead skill audit | T2 (Hermes) |
| #1720 | Phase D: Correction hotspots | T2 (Hermes) |
| #1720 | Phase E: Agent routing intel | T3 (Codex) |
| #1720 | Phase F: Memory deduplication | T2 (Hermes) |
| #1720 | Phase G: Per-repo ecosystem | T3 (Codex) |

## Prompt Files

- T1: `docs/plans/overnight-prompts/2026-04-02/terminal-1-claude-baseline-skillgaps.md`
- T2: `docs/plans/overnight-prompts/2026-04-02/terminal-2-hermes-skills-corrections-memory.md`
- T3: `docs/plans/overnight-prompts/2026-04-02/terminal-3-codex-routing-repoaudit.md`

## What You'll Have by Morning

From Terminal 1 (Claude):
  ✓ Phase A: Cross-agent tool/file frequency baseline (top 50 files, tool distributions, co-occurrence)
  ✓ Phase B: Skill gap candidates (manual workflows that should be skills)

From Terminal 2 (Hermes):
  ✓ Phase C: Dead skill classification (truly-dead / dormant / orphaned across 691 skills)
  ✓ Phase D: Correction hotspot files + test coverage gaps (from 8,965 corrections)
  ✓ Phase F: Memory dedup candidates + AGENTS.md freshness audit (24 repos)

From Terminal 3 (Codex):
  ✓ Phase E: Agent routing recommendations (who handles what best)
  ✓ Phase G: Full 24-repo ecosystem inventory + skill promotion candidates

All outputs in: `analysis/cross-agent-audit-20260402/`

## How to Launch

```bash
# Terminal 1 — Claude Code
cd /mnt/local-analysis/workspace-hub
cat docs/plans/overnight-prompts/2026-04-02/terminal-1-claude-baseline-skillgaps.md | claude

# Terminal 2 — Hermes
cd /mnt/local-analysis/workspace-hub
hermes --prompt-file docs/plans/overnight-prompts/2026-04-02/terminal-2-hermes-skills-corrections-memory.md

# Terminal 3 — Codex
cd /mnt/local-analysis/workspace-hub
cat docs/plans/overnight-prompts/2026-04-02/terminal-3-codex-routing-repoaudit.md | codex
```
