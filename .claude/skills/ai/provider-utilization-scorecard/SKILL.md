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
