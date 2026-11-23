# Skill Invocation Baseline — 2026-04-19

> Generated from `scripts/skills/skill-invocation-scanner.py` (#2320).
> **Source:** `logs/orchestrator/hermes/session_YYYYMMDD.jsonl`.
> **Window:** available retention — 15 days at time of writing.

## Summary

| Metric | Value |
|---|---|
| Total skills discovered (`.claude/skills/**/SKILL.md`) | 2921 |
| Skills with ≥1 distinct session in window | 98 |
| Skills with zero sessions in window | 2823 |
| Coverage days | 15 |
| MIN_COVERAGE_DAYS for tier demotion | 14 |

Because `coverage_days (15) >= 14`, the invocation-signal demotion rule in
`scripts/skills/skill-usage-report.py` IS active: each zero-session skill is
demoted one tier (HOT→WARM, WARM→COLD, COLD→DEAD, DEAD→DEAD).

## Top 20 skills by distinct sessions

| # | Skill | Sessions | Raw events |
|---|---|---|---|
| 1 | `github/github-issues` | 134 | 220 |
| 2 | `coordination/issue-planning-mode` | 95 | 144 |
| 3 | `autonomous-ai-agents/claude-code` | 85 | 125 |
| 4 | `coordination/cross-review-policy` | 61 | 72 |
| 5 | `coordination/session-start-routine` | 57 | 65 |
| 6 | `coordination/gh-work-planning` | 42 | 51 |
| 7 | `coordination/agent-work-adversarial-review` | 33 | 54 |
| 8 | `coordination/workflow-compliance-audit` | 33 | 34 |
| 9 | `coordination/knowledge-source-recon` | 29 | 32 |
| 10 | `software-development/multi-provider-adversarial-review` | 29 | 32 |
| 11 | `coordination/session-corpus-audit` | 28 | 34 |
| 12 | `coordination/provider-session-ecosystem-audit` | 27 | 46 |
| 13 | `software-development/overnight-parallel-agent-prompts` | 27 | 33 |
| 14 | `software-development/gh-work-execution` | 25 | 63 |
| 15 | `coordination/subagent-sandbox-limitations` | 22 | 28 |
| 16 | `coordination/hermes-workflow-audit` | 21 | 25 |
| 17 | `development/planning/writing-plans` | 21 | 22 |
| 18 | `digitalmodel/code-explorer` | 20 | 32 |
| 19 | `development/systematic-debugging` | 18 | 19 |
| 20 | `development/code-reviewer` | 17 | 23 |

## First 20 skills with zero sessions (demotion candidates)

These are candidates for deprecation / consolidation per #2280.

- `_archive/ai/agent-usage-optimizer/baseline-route-mapping-quota-agnostic-defaults`
- `_archive/ai/agent-usage-optimizer/complexity-tier-model-mapping`
- `_archive/ai/agent-usage-optimizer/hours-to-reset-estimation`
- `_archive/ai/agent-usage-optimizer/keyword-route-classification`
- `_archive/ai/agent-usage-optimizer/provider-capability-reference`
- `_archive/ai/agent-usage-optimizer/step-1-read-and-validate-quota-cache`
- `_archive/ai/agent-usage-optimizer/step-2-display-quota-headroom`
- `_archive/ai/agent-usage-optimizer/step-5-work-queue-integration`
- `_archive/ai/agent-usage-optimizer/usage`
- `_archive/ai/agent-usage-optimizer/what-it-does`
- `_archive/ai/prompting/agenta/1-prompt-versioning-and-management`
- `_archive/ai/prompting/agenta/1-prompt-versioning-strategy`
- `_archive/ai/prompting/agenta/2-ab-testing-prompts`
- `_archive/ai/prompting/agenta/3-evaluation-metrics-and-testing`
- `_archive/ai/prompting/agenta/4-playground-and-experimentation`
- `_archive/ai/prompting/agenta/5-model-comparison`
- `_archive/ai/prompting/agenta/6-self-hosted-deployment`
- `_archive/ai/prompting/agenta/connection-issues`
- `_archive/ai/prompting/agenta/fastapi-integration`
- `_archive/ai/prompting/agenta/langchain-integration`

## Known limitations

- 90d classic window is NOT computable: session log retention at time of writing is ~17 days. Output uses `coverage_days` as the actual window.
- Signal is per-machine only. Cross-machine aggregation is future work.
- Events propagate only `skill_name`, `session_id`, `ts`. No file paths, prompts, or tool args are persisted — PII-safe by construction.

Related: #2280 (weekly audit), #2282 (ranking policy).
