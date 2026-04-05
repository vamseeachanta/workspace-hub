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

```bash
h-router-gemini -t terminal,file,web -q "
You are the ACE Engineer advance scout. Working directory: /mnt/local-analysis/workspace-hub.
Execute ALL 5 tasks. Commit after each. Do NOT push. Close each issue.

TASK 1: <description>
- Use search_files or terminal to gather data
- Create: <output file path>
- Commit: git add <file> && git commit -m '...'
- Close: gh issue close <number>

TASK 2-5: same pattern...

RULES: Commit after each task, do NOT push. Close each issue.
All paths under /mnt/local-analysis/workspace-hub/
"
```

Key parameters: 
- `-t terminal,file,web` — enables file system writes and web search
- One session per batch, ~2 min per session, ~$0.00 consumed
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
