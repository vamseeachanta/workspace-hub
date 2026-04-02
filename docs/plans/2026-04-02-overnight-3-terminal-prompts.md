# Overnight 4-Terminal Batch — Cross-Agent Corpus Audit + Agent-to-Skill Conversion

**Date**: 2026-04-02
**Issues**: #1720 (analysis), #1721 (agent-to-skill conversion)
**Machine**: ace-linux-1
**Type**: T1-T3 analysis-only; T4 implementation (creates files + wires config)

## Terminal Allocation

| Terminal | Agent | Issues | Phases | Workload |
|----------|-------|--------|--------|----------|
| T1 | Claude Code | #1720 | A (baseline) + B (skill gaps) | 153K+ Claude JSONL + 691 skills scan |
| T2 | Hermes | #1720 | C (dead skills) + D (corrections) + F (memory) | 547 scored skills + 8,965 corrections + 24 repos |
| T3 | Codex | #1720 | E (routing intel) + G (repo audit) | All 4 agents' logs + 24 repo ecosystem |
| T4 | Hermes | #1721 | Agent→skill conversion | 71+ agent files → SKILL.md + automation script |

## Git Contention Map

```
Terminal 1 writes: analysis/cross-agent-audit-20260402/phase-a-*
                   analysis/cross-agent-audit-20260402/phase-b-*
Terminal 2 writes: analysis/cross-agent-audit-20260402/phase-c-*
                   analysis/cross-agent-audit-20260402/phase-d-*
                   analysis/cross-agent-audit-20260402/phase-f-*
Terminal 3 writes: analysis/cross-agent-audit-20260402/phase-e-*
                   analysis/cross-agent-audit-20260402/phase-g-*
Terminal 4 writes: scripts/skills/convert-agent-to-skill.py
                   scripts/skills/tests/test_convert_agent_to_skill.py
                   config/agents/hermes/config.yaml.template
                   .claude/skills/gsd-agents/ (new)
                   digitalmodel/.claude/skills/ (SEPARATE GIT REPO)
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
| #1721 | Task 1: Conversion script | T4 (Hermes) |
| #1721 | Task 2: digitalmodel P1+P2 | T4 (Hermes) |
| #1721 | Task 3: Wire external_dirs | T4 (Hermes) |
| #1721 | Task 4: GSD template agents | T4 (Hermes) |

## Prompt Files

- T1: `docs/plans/overnight-prompts/2026-04-02/terminal-1-claude-baseline-skillgaps.md`
- T2: `docs/plans/overnight-prompts/2026-04-02/terminal-2-hermes-skills-corrections-memory.md`
- T3: `docs/plans/overnight-prompts/2026-04-02/terminal-3-codex-routing-repoaudit.md`
- T4: `docs/plans/overnight-prompts/2026-04-02/terminal-4-hermes-agent-to-skill-conversion.md`

## What You'll Have by Morning

From Terminal 1 (Claude) — #1720:
  ✓ Phase A: Cross-agent tool/file frequency baseline (top 50 files, tool distributions, co-occurrence)
  ✓ Phase B: Skill gap candidates (manual workflows that should be skills)

From Terminal 2 (Hermes) — #1720:
  ✓ Phase C: Dead skill classification (truly-dead / dormant / orphaned across 691 skills)
  ✓ Phase D: Correction hotspot files + test coverage gaps (from 8,965 corrections)
  ✓ Phase F: Memory dedup candidates + AGENTS.md freshness audit (24 repos)

From Terminal 3 (Codex) — #1720:
  ✓ Phase E: Agent routing recommendations (who handles what best)
  ✓ Phase G: Full 24-repo ecosystem inventory + skill promotion candidates

From Terminal 4 (Hermes) — #1721:
  ✓ convert-agent-to-skill.py reusable script + tests
  ✓ 71+ digitalmodel agents converted to SKILL.md (orcaflex, orcawave, aqwa, freecad, gmsh, cad)
  ✓ ~20 GSD template agents converted to SKILL.md
  ✓ digitalmodel/.claude/skills wired into Hermes external_dirs
  ✓ Hermes skill count: 691 → 780+ skills

All analysis outputs in: `analysis/cross-agent-audit-20260402/`
All new skills in: `digitalmodel/.claude/skills/` + `.claude/skills/gsd-agents/`

## How to Launch

```bash
# Terminal 1 — Claude Code (#1720 analysis)
cd /mnt/local-analysis/workspace-hub
cat docs/plans/overnight-prompts/2026-04-02/terminal-1-claude-baseline-skillgaps.md | claude

# Terminal 2 — Hermes (#1720 analysis)
cd /mnt/local-analysis/workspace-hub
hermes --prompt-file docs/plans/overnight-prompts/2026-04-02/terminal-2-hermes-skills-corrections-memory.md

# Terminal 3 — Codex (#1720 analysis)
cd /mnt/local-analysis/workspace-hub
cat docs/plans/overnight-prompts/2026-04-02/terminal-3-codex-routing-repoaudit.md | codex

# Terminal 4 — Hermes (#1721 conversion)
cd /mnt/local-analysis/workspace-hub
hermes --prompt-file docs/plans/overnight-prompts/2026-04-02/terminal-4-hermes-agent-to-skill-conversion.md
```
