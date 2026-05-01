# Archived Skill: `provider-utilization-scorecard`

Original path: `/home/vamsee/.hermes/skills/ai/provider-utilization-scorecard`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/ai/provider-utilization-scorecard`
Consolidation date: 2026-04-29

---

---
name: provider-utilization-scorecard
description: Refresh provider quota snapshots and generate a weekly Claude/Codex/Gemini utilization scorecard grounded in quota data when available and session-activity fallback when not.
version: 1.0.0
category: ai
type: workflow
triggers:
  - When asked to maximize weekly use of Claude, OpenAI/Codex, and Gemini credits
  - When reviewing whether quota/usage telemetry is sufficient for routing work
  - When maintaining provider utilization scorecards or quota refresh automation
---

# Provider Utilization Scorecard

Use this when the goal is to operationalize weekly credit utilization across Claude, Codex, and Gemini instead of just giving static advice.

## Canonical inputs
- Quota latest snapshot: `config/ai-tools/agent-quota-latest.json`
- Quota history log: `~/.agent-usage/weekly-log.jsonl`
- Provider activity logs: `logs/orchestrator/{claude,codex,hermes,gemini}/session_*.jsonl`
- Provider session audit: `analysis/provider-session-ecosystem-audit.json`
- Human-readable report: `docs/reports/provider-utilization-weekly.md`
- Machine-refresh wrapper log: `logs/quality/provider-utilization-refresh-*.log`

## Canonical commands

Refresh quota + utilization artifacts:
```bash
bash scripts/cron/provider-utilization-refresh.sh
```

Show dashboard:
```bash
uv run --no-project python scripts/ai/credit-utilization-tracker.py --dashboard
```

Reinstall cron if schedule changed:
```bash
bash scripts/cron/setup-cron.sh --replace
crontab -l | grep provider-utilization-refresh
```

Validate tests/schedule:
```bash
uv run pytest tests/analysis/test_credit_utilization_tracker.py tests/cron/test_provider_utilization_refresh.py
uv run --no-project python scripts/cron/validate-schedule.py
```

## Core approach
1. Refresh quota snapshots first using `scripts/ai/assessment/query-quota.sh --refresh --log`.
2. Build the weekly scorecard from both quota snapshots and session-activity exports.
3. Prefer quota-based utilization only when the provider exposes real weekly data.
4. Fall back to activity-vs-recent-peak when quota telemetry is missing or only estimated.
5. Schedule the refresh every 4 hours so weekly utilization is actionable, not stale.

## Interpretation rules
- `utilization_basis=quota` is strongest; use it for routing decisions.
- `utilization_basis=activity_vs_recent_peak` is directional only; use it to spot likely underuse, not exact headroom.
- Hermes is an orchestrator signal, not a paid-provider utilization target.
- Current underutilization alerts should focus on Claude/Codex/Gemini, not Hermes.

## Known provider realities
### Claude
- Real weekly quota may be unavailable in `agent-quota-latest.json` depending on the local source.
- Do not compute fake usage from `pct_remaining` if the snapshot is essentially unavailable.
- If Claude quota is unavailable, report activity fallback explicitly.

### Codex
- `week_messages` and `weekly_limit` from `history.jsonl` are strong enough for real quota-based utilization.
- Codex is usually the cleanest signal for bounded implementation/test workloads.

### Gemini
- Current telemetry may only be `today_messages` / `daily_limit` with `source=estimated`.
- Treat Gemini quota numbers as weak; prefer activity fallback and mark the limitation clearly.

## Critical implementation pitfall
When exported session logs lack runtime `session_id`, DO NOT fall back to a per-record key like `provider:file:tool:ts` for session counts. That massively overcounts sessions. Instead, fall back to the `session_YYYYMMDD.jsonl` file identity so session counts remain sane.

## Another pitfall
Do not treat missing numeric quota fields as zero during snapshot merging. If `week_messages` is absent, keep it absent; otherwise the tracker can incorrectly infer `weekly_limit` usage and produce bogus 100% utilization.

## Outputs to maintain
- `config/ai-tools/provider-utilization-weekly.json`
- `docs/reports/provider-utilization-weekly.md`
- scheduled task `provider-utilization-refresh` in `config/scheduled-tasks/schedule-tasks.yaml`
- wrapper `scripts/cron/provider-utilization-refresh.sh`
- tests:
  - `tests/analysis/test_credit_utilization_tracker.py`
  - `tests/cron/test_provider_utilization_refresh.py`

## Recommended follow-on work
After the scorecard exists, the next high-value layer is routing automation:
- if Codex utilization is low, surface bounded implementation/test/refactor work
- if Gemini utilization is low, surface research/recon/risk-scan batches
- if Claude utilization is low and quota is trustworthy, route adversarial review and long-context synthesis there

## Weekly credit-burn operating model

When the user asks to maximize provider credits across Claude/Codex/Gemini, convert the scorecard into an executable package pipeline, not just a narrative report.

Target burn curve for providers with real weekly quotas:
- Day 1: 18% cumulative
- Day 2: 36% cumulative
- Day 3: 54% cumulative
- Day 4: 72% cumulative
- Day 5: 90% cumulative
- Days 6-7: preserve the final 10% for failures, review, CI repair, and closeout

For providers with daily caps instead of true weekly front-loadable quotas, do not claim 90% weekly by day 5 if the math is impossible. Example: Gemini at 1000/day can only reach 5/7 = 71.4% of a seven-day total by day 5. Manage those as daily burn targets instead: use roughly 80-90% of each day’s capacity with a small reserve.

## Always-ready package queues

To keep feature/issue work continuously executable as long as AI credits remain, maintain four queues:

1. Recon-ready Gemini packages
   - target inventory: 10-15 packages
   - package size: 5-6 related research/recon/source tasks per session
   - focus: raw data, standards/source discovery, competitor/GTM scans, wiki gap discovery, issue expansion

2. Plan-review packages
   - target inventory: 10+ issues in or near plan-review
   - focus: feeding the approval pipeline before implementation capacity runs dry

3. Plan-approved Codex implementation packages
   - target inventory: 8-12 approved packages
   - focus: bounded implementation, tests, calculation modules, parametric outputs, CI/harness repair, static-site/GTM slices
   - if Codex utilization is low, this queue is usually the bottleneck, not Codex capacity

4. Implementation-review / closeout packages
   - target inventory: 5-8 packages
   - focus: adversarial implementation review, CI evidence, closeout comments, future-issue extraction

## Value-chain routing model

For the recurring ACE/workspace-hub pipeline, route work by value-chain stage:

- raw data -> llm-wiki: Gemini for source discovery and gap scans; Claude for contracts/review; Codex for promotion pipeline/checkers/tests
- llm-wiki -> calculation code: Claude for semantic contracts and plan review; Codex for TDD implementation; Gemini for standards/source cross-checks
- calculation code -> parametric outputs: Codex for generators, reports, dashboards, and tests; Claude for acceptance review; Gemini for benchmark/reference scans
- parametric outputs -> website/GTM: Gemini for prospect/company research; Codex for page/data/CTA implementation; Claude for narrative synthesis and final GTM review
- control-plane enablers: Codex for review-runner/harness fixes, Claude for governance/review, Gemini for audit/recon only

## Package lifecycle gate

Every provider package should follow:
GitHub issue -> resource intelligence -> canonical plan -> adversarial plan review -> user approval -> status:plan-approved -> implementation -> adversarial implementation review -> closeout.

Never dispatch implementation from status:plan-review. A package is execution-ready only when it has a GitHub issue, canonical plan under docs/plans, plan review artifacts, explicit approval, status:plan-approved, an agent/provider label, and clear closeout criteria.

## Dispatch rule

Use this loop after refreshing the scorecard:
- If Codex is below the burn line, dispatch the next status:plan-approved implementation/test/refactor package.
- If Gemini daily use is below target, dispatch the next 5-6 task recon/research batch.
- If Claude has review backlog, dispatch plan or implementation review packages.
- If no approved implementation work exists, pause coding and spend Claude/Gemini on refilling the plan-review and approval pipeline.
- If a provider is ahead of target, reserve it for reviews, failures, and closeout.
