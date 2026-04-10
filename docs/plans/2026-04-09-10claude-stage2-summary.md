# 2026-04-09 10-Claude Stage 2 Overnight Pack

Purpose: preserve Codex credits and keep all overnight work on Claude only.

This batch assumes workspace-hub currently has zero open issues with `status:plan-approved`, so every terminal is planning-only. Each terminal reads one existing dossier from `docs/plans/overnight-prompts/2026-04-09-10claude/results/` and writes one new operator-ready execution pack under `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/`.

Rules for every terminal:
- Use Claude only.
- Do not implement production code.
- Do not mutate GitHub state.
- Do not ask the user questions.
- Write exactly one result file in your assigned path.
- Use `uv run` for Python if needed.

Issue-to-terminal map:
| Issue | Workstream | Terminal |
|---:|---|---|
| #2063 | drilling riser analysis | T1 |
| #2062 | drilling rig fleet adapter | T2 |
| #2060 | timeline benchmarks | T3 |
| #2059 | vessel stability cases | T4 |
| #2058 | subsea architecture patterns | T5 |
| #2057 | governance phase 3 infrastructure | T6 |
| #2056 | governance phase 2 runtime hooks | T7 |
| #2055 | subsea cost benchmarking | T8 |
| #2054 | decline-curve cashflows | T9 |
| #2053 | concept selection matrix | T10 |

Contention map:
- T1 writes: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-1-drilling-riser-execution-pack.md
- T2 writes: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-2-drilling-rig-execution-pack.md
- T3 writes: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-3-timeline-benchmarks-execution-pack.md
- T4 writes: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-4-vessel-stability-execution-pack.md
- T5 writes: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-5-architecture-patterns-execution-pack.md
- T6 writes: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-6-governance-phase3-execution-pack.md
- T7 writes: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-7-governance-phase2-execution-pack.md
- T8 writes: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-8-subsea-cost-execution-pack.md
- T9 writes: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-9-decline-curve-execution-pack.md
- T10 writes: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-10-concept-selection-execution-pack.md
- Zero overlap by design.

Expected morning deliverables:
- 10 operator-ready execution packs
- exact `gh issue comment`, `gh issue edit`, and label command drafts for each issue
- one implementation prompt per issue, ready to paste into a future Claude run after plan approval
- blocker/assumption summary per issue
