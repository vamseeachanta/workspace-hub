---
name: agent-usage-optimizer
version: "1.0.0"
category: ai
description: "Reads quota state and recommends optimal Claude/Codex/Gemini allocation per task"
capabilities:
  - quota-aware routing
  - route-mapping
  - headroom display
requires:
  - ~/.cache/agent-quota.json
see_also:
  - ai/optimization/model-selection
  - ai/optimization/usage-optimization
---

# AI Agent Usage Optimizer

> Version: 1.0.0
> Category: AI / Optimization
> Triggers: `/agent-alloc` — run before any session with multiple work items

## When to Use

- Before starting a work session with 3+ queued WRK items
- When Claude quota is approaching a constraint (< 50% remaining)
- When routing a task and unsure which provider fits best
- After `/session-start` to set provider allocation for the session

## Usage

```
/agent-alloc                     — show quota headroom + routing for work queue
/agent-alloc [task description]  — recommend provider for a specific ad-hoc task
/agent-alloc route-a             — show recommended providers for Route A items
/agent-alloc route-b             — show recommended providers for Route B items
/agent-alloc route-c             — show recommended providers for Route C items
```

## What It Does

1. Reads `~/.cache/agent-quota.json` — no external calls if cache age < 1 hour
2. Displays quota headroom per provider: % remaining + estimated hours to daily reset
3. Applies routing rules based on quota state and task complexity
4. Recommends primary + secondary provider with rationale
5. Flags any provider critically low (< 20% remaining)
6. Shows as pre-gate output before the plan gate when used with `/work run`

---

## Step 1 — Read and Validate Quota Cache

```bash
QUOTA_FILE="$HOME/.cache/agent-quota.json"

# Check cache exists and is fresh (< 1 hour old)
if [[ ! -f "$QUOTA_FILE" ]]; then
  echo "WARN: quota cache not found at $QUOTA_FILE"
  echo "Run: bash scripts/monitoring/query-quota.sh"
  echo "Falling back to default routing rules."
  CACHE_FRESH=false
else
  CACHE_AGE_SECS=$(( $(date +%s) - $(date -r "$QUOTA_FILE" +%s) ))
  if [[ $CACHE_AGE_SECS -gt 3600 ]]; then
    echo "WARN: quota cache is $(( CACHE_AGE_SECS / 60 ))m old — consider refreshing"
    CACHE_FRESH=false
  else
    CACHE_FRESH=true
  fi
fi

# Parse quota values (requires jq)
CLAUDE_PCT=$(jq -r '.agents[] | select(.provider=="claude") | .pct_remaining' "$QUOTA_FILE" 2>/dev/null || echo 100)
CODEX_PCT=$(jq  -r '.agents[] | select(.provider=="codex")  | .pct_remaining' "$QUOTA_FILE" 2>/dev/null || echo 100)
GEMINI_PCT=$(jq -r '.agents[] | select(.provider=="gemini") | .pct_remaining' "$QUOTA_FILE" 2>/dev/null || echo 100)
CACHE_TS=$(jq  -r '.timestamp' "$QUOTA_FILE" 2>/dev/null || echo "unknown")
```

## Step 2 — Display Quota Headroom

Render quota headroom table from the parsed values above.

```
Provider      │ % Remaining │ Status      │ Best for
──────────────┼─────────────┼─────────────┼──────────────────────────────────
Claude Opus   │  <CLAUDE>%  │  <STATUS>   │ Architecture, compound reasoning
Claude Sonnet │  <CLAUDE>%  │  <STATUS>   │ Standard tasks, code review
Claude Haiku  │  <CLAUDE>%  │  <STATUS>   │ Bulk ops, summaries (cost-save)
Codex         │  <CODEX>%   │  <STATUS>   │ Focused code gen, unit tests
Gemini        │  <GEMINI>%  │  <STATUS>   │ Long-context, large file review

Cache: <CACHE_TS>   Fresh: <CACHE_FRESH>
```

Status thresholds:
- >= 50%  → OK (green)
- 20-49%  → LOW (yellow) — prefer alternatives for heavy tasks
- < 20%   → CRITICAL (red) — steer away, flag before routing

## Step 3 — Provider Allocation Rules

### Baseline Route Mapping (quota-agnostic defaults)

| Route | Complexity | Primary         | Secondary        | Use For                              |
|-------|-----------|-----------------|------------------|--------------------------------------|
| A     | Simple    | Codex           | Claude Haiku     | Focused code gen, unit tests, debug  |
| B     | Standard  | Claude Sonnet   | Codex            | Reviews, docs, standard features     |
| C     | Compound  | Claude Opus     | Claude Sonnet    | Architecture, multi-file refactors   |
| —     | Bulk      | Claude Haiku    | Gemini           | Summarisation, data processing       |
| —     | Long-ctx  | Gemini          | Claude Sonnet    | Large file review, cross-repo scan   |

### Quota-Adjusted Routing

Apply these overrides on top of baseline when quota thresholds are triggered:

```
IF claude_pct < 20%:
  Route B primary → Codex  (demote Sonnet; fallback secondary = Gemini)
  Route C primary → Gemini (demote Opus;   fallback secondary = Codex)
  Emit CRITICAL warning before plan gate

ELIF claude_pct < 50%:
  Route C primary remains Opus  (preserve for compound/architecture only)
  Route B primary → Codex       (save Sonnet for Route C overflow)
  Emit LOW warning before plan gate

ELSE (claude_pct >= 50%):
  Use baseline route mapping above (Claude is the preferred quality provider)

ALWAYS:
  Bulk operations → Claude Haiku regardless of quota level
  Long-context    → Gemini first when file count > 10 or token estimate > 50K
```

## Step 4 — Per-Task Recommendation (ad-hoc mode)

When invoked as `/agent-alloc [task description]`, classify by keywords then apply quota routing:

### Keyword → Route classification

```
Compound / Route C keywords:
  architecture, design, system, multi-file, refactor, security review,
  cross-repo, orchestrat, compound, plan, spec

Standard / Route B keywords:
  implement, feature, review, documentation, test, bug, fix, config,
  update, migrate, integration

Simple / Route A keywords:
  generate, scaffold, unit test, snippet, function, debug, format,
  check, validate, search, grep

Bulk keywords:
  summarise, summarize, batch, bulk, all files, across repos, report

Long-context keywords:
  large file, full repo, 1000 lines, entire codebase, cross-repo scan
```

Output format for ad-hoc recommendation:

```
Task: "implement OAuth login for the API"
Route: B (Standard)

  Primary:    Claude Sonnet  [quota: <CLAUDE>% — OK]
  Secondary:  Codex          [quota: <CODEX>%  — OK]

  Rationale: Standard feature implementation with moderate complexity.
             Sonnet provides quality output within quota headroom.
             Codex is secondary for focused function-level generation.
```

## Step 5 — Work Queue Integration

When showing recommendations before the plan gate in `/work run`:

```
=== Agent Allocation Check ===
Cache age: 12m  |  Claude: 73%  |  Codex: 100%  |  Gemini: 100%

Next 3 queue items:
  WRK-301 [Route B] → Claude Sonnet (primary),  Codex (secondary)
  WRK-302 [Route A] → Codex (primary),          Claude Haiku (secondary)
  WRK-303 [Route C] → Claude Opus (primary),    Claude Sonnet (secondary)

No providers critical. Proceeding to plan gate.
==============================
```

If any provider is critical (< 20%), show:

```
=== Agent Allocation Check ===
[CRITICAL] Claude quota at 14% — Routes B and C rerouted.

  WRK-301 [Route B] → Codex (primary),   Gemini (secondary)   [rerouted]
  WRK-302 [Route A] → Codex (primary),   Claude Haiku (sec)
  WRK-303 [Route C] → Gemini (primary),  Codex (secondary)    [rerouted]

Approve rerouted allocation? (y/n)
==============================
```

## Provider Capability Reference

| Provider       | Strengths                                          | Avoid When                          |
|----------------|----------------------------------------------------|-------------------------------------|
| Claude Opus    | Architecture, deep reasoning, compound tasks       | Quota < 20%; simple tasks           |
| Claude Sonnet  | Standard code, reviews, balanced quality/speed     | Quota < 20% and Route C needed      |
| Claude Haiku   | Bulk data, summarisation, cost-effective volume    | Architecture or security decisions  |
| Codex          | Focused code gen, unit tests, debugging functions  | Long-context docs; planning work    |
| Gemini         | Long-context analysis, large files, cross-repo     | Fine-grained code edits             |

## Hours-to-Reset Estimation

Daily limits reset at midnight UTC. Calculate approximate headroom time:

```bash
NOW_SECS=$(date -u +%s)
MIDNIGHT_SECS=$(date -u -d "tomorrow 00:00:00" +%s 2>/dev/null \
                || date -u -v+1d -j -f "%H:%M:%S" "00:00:00" +%s)
HOURS_TO_RESET=$(( (MIDNIGHT_SECS - NOW_SECS) / 3600 ))
echo "Hours to daily reset: ${HOURS_TO_RESET}h"
```

---

*Use this skill before any multi-item work session or when quota is a concern.*
*Related: `ai/optimization/model-selection`, `ai/optimization/usage-optimization`*
