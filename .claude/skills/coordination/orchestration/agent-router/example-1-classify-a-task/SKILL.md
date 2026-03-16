---
name: agent-router-example-1-classify-a-task
description: 'Sub-skill of agent-router: Example 1: Classify a Task (+4).'
version: 2.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Example 1: Classify a Task (+4)

## Example 1: Classify a Task


```bash
$ ./scripts/coordination/routing/route.sh -q "What is a mooring line?"
{
  "classification": {
    "tier": "SIMPLE",
    "confidence": 0.92,
    "primary_provider": "codex"
  },
  "routing": {
    "provider": "codex",
    "auto_route": true
  }
}
```

## Example 2: Route a Work Queue Item


```bash
$ ./scripts/coordination/routing/route.sh --wrk WRK-110
Work item: WRK-110
Task: Implement fatigue analysis pipeline
--- Classifying task ---
Tier: STANDARD | Confidence: 0.65 | Classifier suggests: codex
Routed to: codex (Primary provider available)
```

## Example 3: Show Routing Stats


```bash
$ ./scripts/coordination/routing/route.sh --stats
=== Routing Decision History ===
Total decisions: 42

Per-provider counts:
  18 claude
  15 codex
   9 gemini


*See sub-skills for full details.*

## Example 4: Rate an Agent (with model)


```bash
# Rate after task completion (auto-detects last routed provider + model)
$ ./scripts/coordination/routing/route.sh --rate 5

# Rate a specific provider
$ ./scripts/coordination/routing/route.sh --rate 4 claude
Rated claude/opus-4-6: 4/5

# Rate a specific model
$ ./scripts/coordination/routing/route.sh --rate 3 gemini/gemini-flash
Rated gemini/gemini-flash: 3/5
```

## Example 5: View Per-Model EWMA Stats


```bash
$ ./scripts/coordination/routing/route.sh --stats
...
=== Model Performance (EWMA) ===
  claude/opus-4-6:        4.200/5 (12 ratings)
  claude/sonnet-4-5:      3.800/5 (5 ratings)
  codex/codex-cli:        4.000/5 (8 ratings)
  gemini/gemini-pro:      3.500/5 (6 ratings)
  gemini/gemini-flash:    3.100/5 (3 ratings)

=== Per-Tier Model Performance ===
  COMPLEX: claude/opus-4-6 (4.500) gemini/gemini-pro (3.600)
  REASONING: claude/opus-4-6 (4.100)
```
