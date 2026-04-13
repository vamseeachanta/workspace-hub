---
name: agent-usage-optimizer
version: 1.0.0
category: ai
description: Reads quota state and recommends optimal Claude/Codex/Gemini allocation
  per task
type: reference
capabilities:
- quota-aware routing
- route-mapping
- headroom display
requires:
- ~/.cache/agent-quota.json
tags:
- quota-management
- multi-provider
- routing
- claude
- codex
- gemini
- gemini-batching
- agent-labels
---

# Agent Usage Optimizer

## Agent Routing via GitHub Labels (Preferred Method)

Deterministic agent routing using `agent:` labels on GitHub issues — no separate queue file needed:

```bash
# Route tasks to agents via labels
gh issue edit <issue-number> --add-label "agent:gemini"
gh issue edit <issue-number> --add-label "agent:claude"  
gh issue edit <issue-number> --add-label "agent:codex"
```

View agent queues:
```bash
gh issue list --label "agent:gemini,priority:high"
gh issue list --label "agent:claude,priority:high"
gh issue list --label "agent:codex,priority:high"
```

Reassign tasks:
```bash
gh issue edit <issue-number> --remove-label "agent:gemini" --add-label "agent:claude"
```

## Gemini Batched Session Pattern (Maximize $20/mo Quota)

Group 5-6 related research/planning tasks into ONE Gemini session. Each task produces a file + commit.

### Working Methods

**Option A — OpenRouter (recommended for non-interactive/overnight):**
```bash
hermes chat --provider openrouter --model google/gemini-2.5-pro --quiet -q "
You are the ACE Engineer advance scout. Working directory: /mnt/local-analysis/workspace-hub.
<task description>
"
```
This works reliably for one-shot/overnight execution. Costs OpenRouter credits but avoids 403 errors.

**Option B — Interactive session (Copilot provider):**
```bash
hermes chat --provider copilot --model gemini-2.5-pro -q "task"
```
Only works in interactive mode with --yolo flag for unattended runs.

### BROKEN: Do NOT Use
- `h-router-gemini -q` — alias does not work for one-shot
- `hermes chat --provider copilot --model gemini-2.5-pro --quiet -q` — returns HTTP 403
- `hermes chat --provider copilot --model gemini-2.5-pro -q` (interactive) — returns HTTP 403
- Copilot/ GitHub's Gemini API blocks non-interactive CLI calls entirely

### Verified Working Gemini Providers
| Provider | Model | Interactive | One-shot (-q) | Notes |
|----------|-------|-------------|---------------|-------|
| openrouter | google/gemini-2.5-pro | Yes | Yes | Recommended for batches |
| copilot | gemini-2.5-pro | Yes (with --yolo) | No (403) | Only for interactive sessions |

### Overnight Gemini Pattern
For overnight batches, use openrouter provider or delegate to subagents (which run on current model):
```bash
# Per-task Gemini execution:
hermes chat --provider openrouter --model google/gemini-2.5-pro --quiet -q "<self-contained-prompt>"

# Or use subagent (runs on current model, NOT Gemini):
# delegate_task(goal="research task", toolsets=["terminal", "file"])
```

Key parameters:
- `--quiet` — suppresses banners for programmatic use
- `--provider openrouter --model google/gemini-2.5-pro` — working Gemini path
- One session per batch, ~2 min per session
- Gemini handles web_search, file reads, file writes, git commits natively

## Claude/Codex Implementation Pattern

For heavy coding tasks, use:
```bash
# Complex implementation (Claude Opus)
hermes chat --provider anthropic -m claude-opus-4-6 -q "<task>"

# Bounded tests + review (Codex via OpenAI)
hermes chat --provider openai-codex -q "<task>"
```

## When to Use

- Before starting a work session with 3+ queued WRK items
- When Claude quota is approaching a constraint (< 50% remaining)
- When routing a task and unsure which provider fits best
- After `/session-start` to set provider allocation for the session

## Telemetry Sufficiency Check (do this before claiming "optimize to 100% weekly")

Do not assume session logs alone are enough to optimize quota burn. First verify all three layers:

1. Live quota snapshot
   - Run:
   ```bash
   bash scripts/ai/assessment/query-quota.sh --refresh --json
   ```
   - Inspect `config/ai-tools/agent-quota-latest.json`
   - Treat these states as insufficient for hard utilization targets:
     - Claude `source: unavailable`
     - Gemini `source: estimated`
     - missing/null `week_pct`, `pct_remaining`, `hours_to_reset`

2. Historical quota ledger freshness
   - Check `~/.agent-usage/weekly-log.jsonl`
   - If the file exists but has not been updated recently, you do NOT have enough telemetry for weekly pacing even if session logs are rich.
   - A stale quota ledger means you can still do routing guidance, but not reliable week-to-target burn-down.

3. Session coverage freshness
   - Export native sessions before analysis:
   ```bash
   bash scripts/cron/hermes-session-export.sh
   bash scripts/cron/codex-session-export.sh
   bash scripts/cron/gemini-session-export.sh
   bash scripts/cron/provider-session-ecosystem-audit.sh
   ```
   - Then use `analysis/provider-session-ecosystem-audit.json` and `docs/reports/provider-session-ecosystem-audit.md` for actual usage patterns.

## Practical Interpretation Rules

- If quota telemetry is weak but session telemetry is strong:
  - You have enough data to strengthen the repo ecosystem now.
  - You do NOT have enough data to guarantee near-100% weekly credit utilization.
- If Codex shows real quota data and low migration debt, push more bounded implementation/test/refactor work to Codex.
- If Gemini recent session volume is tiny and quota is only estimated, treat Gemini as underused research capacity and batch reconnaissance/risk-analysis work there.
- If Claude quota is unavailable, avoid promising precise Claude weekly pacing; use Claude primarily for high-value long-context planning/review until telemetry is fixed.

## Scheduling Gap Check

Before trusting the optimizer, verify quota logging is actually scheduled. In practice, it is easy to have:
- `scripts/ai/assessment/query-quota.sh`
- `config/ai-tools/agent-quota-latest.json`
- `~/.agent-usage/weekly-log.jsonl`

but no scheduled task keeping them fresh.

Check `config/scheduled-tasks/schedule-tasks.yaml` for explicit quota-refresh / usage-log jobs. If missing, record that as a telemetry gap and do not overstate optimization confidence.

## Operationalized control-plane artifacts

A reusable provider-utilization control plane now exists in workspace-hub. Prefer these generated artifacts over ad hoc interpretation when deciding where to route work:

- `config/ai-tools/provider-utilization-weekly.json`
- `docs/reports/provider-utilization-weekly.md`
- `config/ai-tools/provider-routing-scorecard.json`
- `docs/reports/provider-routing-scorecard.md`
- `config/ai-tools/provider-work-queue.json`
- `docs/reports/provider-work-queue.md`
- `config/ai-tools/provider-autolabel-candidates.json`
- `docs/reports/provider-autolabel-candidates.md`
- handoff/reference snapshot: `docs/reports/provider-routing-system-handoff-YYYY-MM-DD.md`

Supporting scripts:
- `scripts/ai/credit-utilization-tracker.py`
- `scripts/ai/provider-routing-scorecard.py`
- `scripts/ai/provider-work-queue.py`
- `scripts/ai/provider-autolabel.py`
- wrapper: `scripts/cron/provider-utilization-refresh.sh`

The scheduled task is:
- `provider-utilization-refresh` in `config/scheduled-tasks/schedule-tasks.yaml`

## Recommended operational loop

Use this order:
1. Refresh telemetry and derived routing artifacts:
```bash
bash scripts/cron/provider-utilization-refresh.sh
```
2. Read the routing scorecard to decide provider order.
3. Read the provider work queue to see issue candidates by provider.
4. Review the autolabel candidate report.
5. Only then consider applying labels.

## Conservative auto-labeling rule

Auto-labeling should remain conservative. The current reusable pattern is:
- only consider issues with no existing `agent:*` label
- only label high-confidence candidates
- prefer execution-ready issues (`status:plan-approved`) first
- require strong provider-specific routing reasons, not just generic keyword matches
- apply only a small bounded batch per run

Current command pattern:
```bash
# Dry run
uv run --no-project python scripts/ai/provider-autolabel.py

# Conservative live apply
uv run --no-project python scripts/ai/provider-autolabel.py --apply --limit 3
```

Confidence threshold lessons from live use:
- `>= 0.90` is reasonable for safe automatic labeling
- around `0.60` is still useful for reporting, but not for automatic label application

## Provider-specific practical guidance from live telemetry

- Codex: best lane for bounded implementation, tests, repair, cleanup, refactors. If underused and quota is visible, push more execution here first.
- Gemini: best lane for batched research/recon/risk-analysis packets. Do not auto-label aggressively until Gemini confidence logic is stronger than simple keyword matching.
- Claude: keep for adversarial review, planning, long-context synthesis, architecture, and governance-heavy work. Avoid burning Claude on mechanical loops Codex can absorb.

## Follow-on improvement areas

If the control plane is working but still imperfect, the next high-value upgrades are:
- add explanatory GitHub comments when high-confidence auto-labels are applied
- strengthen Gemini-specific routing confidence using research-readiness signals, not just broad research keywords
- improve Claude/Gemini quota observability so utilization can be exact rather than heuristic

## Sub-Skills

When the goal is not just analysis but active weekly credit utilization, use this artifact chain:

1. Refresh quota + utilization artifacts
```bash
bash scripts/cron/provider-utilization-refresh.sh
```
This should regenerate:
- `config/ai-tools/provider-utilization-weekly.json`
- `docs/reports/provider-utilization-weekly.md`
- `config/ai-tools/provider-routing-scorecard.json`
- `docs/reports/provider-routing-scorecard.md`
- `config/ai-tools/provider-work-queue.json`
- `docs/reports/provider-work-queue.md`
- `config/ai-tools/provider-autolabel-candidates.json`
- `docs/reports/provider-autolabel-candidates.md`

2. Read the routing scorecard for provider-level guidance
- `provider-routing-scorecard.json` combines current-week utilization with provider session audit hygiene
- it should answer:
  - who is underused now
  - what work each provider should receive next
  - which providers have hygiene debt that would waste credits

3. Read the provider work queue for live issue routing
- `provider-work-queue.json` combines the scorecard with live `gh issue list` data
- prefer `status:plan-approved` issues first
- respect existing `agent:*` labels as authoritative when present
- treat the generated per-provider issue lists as the primary dispatch surface

## Confidence-weighted auto-labeling rule

Auto-labeling GitHub issues is useful, but only if conservative.

Use this pattern:
- generate candidates in dry-run mode first:
```bash
uv run --no-project python scripts/ai/provider-autolabel.py
```
- only apply labels for issues with strong confidence:
```bash
uv run --no-project python scripts/ai/provider-autolabel.py --apply --limit 3
```

Recommended guardrails:
- never touch issues that already have an `agent:*` label
- require high confidence (>= 0.90 worked well in practice)
- prefer issues that are already `status:plan-approved`
- require a strong routing reason, not a weak heuristic match
- cap live application to a small number per run (`--limit 3`) until confidence is proven over multiple cycles

High-confidence pattern observed in practice:
- execution-ready issue
- strong language match
  - Codex: implementation/test/fix
  - Claude: strategy/workflow/architecture
  - Gemini: research/triage/audit
- provider currently underused according to the scorecard
- no pre-existing agent label

Do NOT auto-label broad or ambiguous items just because the provider is underused.

## Practical dispatch rules from the scorecard

For current workspace-hub-style ecosystems, these rules proved reusable:
- Codex: push bounded implementation, tests, refactors, and crisp execution-ready issues first
- Claude: reserve for adversarial review, governance, orchestration, and long-context strategy
- Gemini: use for batched research/recon/risk-analysis packets; do not rely on Gemini telemetry as exact weekly headroom if the quota source is only estimated

## Sub-Skills

When the repo already has provider session exports and a provider audit, do not stop at a narrative recommendation. Build a 3-layer control loop:

1. Utilization layer
   - Generate weekly utilization artifacts from:
     - `config/ai-tools/agent-quota-latest.json`
     - `~/.agent-usage/weekly-log.jsonl`
     - `logs/orchestrator/*/session_*.jsonl`
   - Canonical outputs:
     - `config/ai-tools/provider-utilization-weekly.json`
     - `docs/reports/provider-utilization-weekly.md`
   - Prefer real quota-based utilization when available (`week_messages/weekly_limit`, `week_pct`)
   - Fall back to `activity_vs_recent_peak` when quota telemetry is weak

2. Routing-scorecard layer
   - Combine utilization outputs with `analysis/provider-session-ecosystem-audit.json`
   - Canonical outputs:
     - `config/ai-tools/provider-routing-scorecard.json`
     - `docs/reports/provider-routing-scorecard.md`
   - Include per provider:
     - current reported utilization
     - quota basis / source
     - missing repo reads
     - python3-per-1k density
     - migration-debt density
     - preferred work types
     - avoid-work types
     - recommended actions
   - Use this to produce a ranked provider order (for example: `gemini, codex, claude`)

3. Live issue-queue layer
   - Read open GitHub issues with `gh issue list --state open --limit 200 --json ...`
   - Combine live issues with the routing scorecard
   - Canonical outputs:
     - `config/ai-tools/provider-work-queue.json`
     - `docs/reports/provider-work-queue.md`
   - Group issues by recommended provider
   - Respect existing `agent:*` labels first
   - Only use heuristics when no explicit agent label exists
   - Sort execution-ready items first (`status:plan-approved` or explicit agent ownership)

## Recommended heuristics for provider-specific work routing

- Claude
  - best for: adversarial plan review, adversarial implementation review, long-context synthesis, repo strategy, architecture, workflow/governance-heavy work
  - avoid: bounded test-fix loops, mechanical refactors, commodity grep/read sweeps
  - if stale-path drift / migration debt is high, reduce wasted reads before increasing Claude load

- Codex
  - best for: bounded implementation, test writing/repair, mechanical cleanup/refactors, crisp issue execution
  - if quota telemetry is real and utilization is low, this should become the default overflow execution lane

- Gemini
  - best for: batched research/recon, risk enumeration, competitor/standards scans, issue expansion and scouting
  - if telemetry is only estimated, treat utilization as directional, but still use Gemini as the underused research lane
  - batch 5-6 related recon tasks into a single Gemini session when possible

## Safe mutation rule for GitHub labels

Do NOT mass-apply `agent:` labels just because the scorecard exists.

Preferred sequence:
1. generate utilization artifacts
2. generate routing scorecard
3. generate provider work queue
4. manually inspect the top routed issues per provider
5. only then apply `agent:` labels to the clearest cases

Reason:
- routing heuristics are useful earlier than they are trustworthy for broad backlog mutation
- existing explicit labels should always override heuristic routing
- reporting/queueing is low risk; mass relabeling is not

## Refresh pipeline pattern

A good recurring wrapper should:
1. run `bash scripts/ai/assessment/query-quota.sh --refresh --log`
2. run the utilization tracker
3. run the routing scorecard generator
4. run the provider work queue generator
5. verify all expected JSON/Markdown outputs exist
6. log to `logs/quality/provider-utilization-refresh-YYYYMMDD.log`

A practical schedule is every 4 hours.

## Implementation gotcha learned in practice

When aggregating provider activity from exported `session_*.jsonl` logs, older exports may not include reliable runtime `session_id` values. If you fall back to per-record keys like `tool + ts`, you will massively overcount sessions.

Safer fallback:
- if `session_id` exists, use it
- otherwise, fall back to the `session_YYYYMMDD` file identity rather than the individual record identity

This keeps session counts directionally sane even when older exported logs are coarse.

## Sub-Skills

When the repo already contains session exports plus provider audit artifacts, the most reusable pattern is:

1. Refresh quota snapshots and append the weekly quota ledger:
```bash
bash scripts/ai/assessment/query-quota.sh --refresh --log
```
2. Refresh exported provider-session artifacts first when needed:
```bash
bash scripts/cron/hermes-session-export.sh
bash scripts/cron/codex-session-export.sh
bash scripts/cron/gemini-session-export.sh
bash scripts/cron/provider-session-ecosystem-audit.sh
```
3. Build weekly utilization artifacts:
```bash
uv run --no-project python scripts/ai/credit-utilization-tracker.py \
  --weeks 8 \
  --output-json config/ai-tools/provider-utilization-weekly.json \
  --output-md docs/reports/provider-utilization-weekly.md
```
4. Build routing guidance from utilization + audit hygiene:
```bash
uv run --no-project python scripts/ai/provider-routing-scorecard.py
```

Canonical outputs:
- `config/ai-tools/provider-utilization-weekly.json`
- `docs/reports/provider-utilization-weekly.md`
- `config/ai-tools/provider-routing-scorecard.json`
- `docs/reports/provider-routing-scorecard.md`

## Interpretation Rules for the New Scorecard

Use the routing scorecard to decide where the next work packets go:
- `codex` underused + quota visible + low migration debt -> route bounded implementation, tests, cleanup, crisp issue execution there first
- `gemini` underused + weak/estimated telemetry -> route batched research/recon/risk-analysis packets there, but treat capacity as directional rather than exact
- `claude` underused + high stale-read debt -> reserve for adversarial review, plan review, and long-context synthesis; reduce stale-path drift before trying to scale load there

Recommended practical ordering in workspace-hub is not purely "lowest utilization first". Combine:
- underutilization
- telemetry confidence
- migration debt / stale-read density
- work-type fit

That is why Gemini and Codex may both rank ahead of Claude even when Claude appears idle.

## Recurring Automation Pattern

In workspace-hub this is now best run via:
- wrapper: `scripts/cron/provider-utilization-refresh.sh`
- schedule task id: `provider-utilization-refresh`
- cron log: `logs/quality/provider-utilization-refresh-*.log`

The wrapper should always verify that all four artifacts exist after generation, not just the quota snapshot and utilization report.

## Tracker Implementation Gotchas

Lessons learned while operationalizing this:
- prefer quota-based utilization only when the basis is real weekly quota (`week_pct` or `week_messages/weekly_limit`)
- do not treat `pct_remaining` from an `unavailable` source as trustworthy weekly utilization
- Gemini `today_messages/daily_limit` from `estimated` is useful only as a weak hint; keep activity fallback active
- when exported orchestrator logs lack runtime `session_id`, do NOT derive session counts from per-record timestamps/tool names or you will massively overcount sessions; fall back to file identity instead
- for routing, activity alone is not enough; combine utilization with audit hygiene (`missing_repo_reads`, migration-debt hints, python3 density)

## Sub-Skills

- [Usage](usage/SKILL.md)
- [What It Does](what-it-does/SKILL.md)
- [Step 1 — Read and Validate Quota Cache](step-1-read-and-validate-quota-cache/SKILL.md)
- [Step 2 — Display Quota Headroom](step-2-display-quota-headroom/SKILL.md)
- [Baseline Route Mapping (quota-agnostic defaults) (+1)](baseline-route-mapping-quota-agnostic-defaults/SKILL.md)
- [Keyword → Route classification](keyword-route-classification/SKILL.md)
- [Step 5 — Work Queue Integration](step-5-work-queue-integration/SKILL.md)
- [Provider Capability Reference](provider-capability-reference/SKILL.md)
- [Hours-to-Reset Estimation](hours-to-reset-estimation/SKILL.md)
- [Complexity Tier → Model Mapping](complexity-tier-model-mapping/SKILL.md)
