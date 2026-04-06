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
