---
name: core-context-management-response-format-rules
description: 'Sub-skill of core-context-management: Response Format Rules (+3).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# Response Format Rules (+3)

## Response Format Rules


#### Output Constraints
- **Tables**: Maximum 10 rows, summarize remainder
- **Code blocks**: Maximum 50 lines, split larger into files
- **Lists**: Maximum 15 items, aggregate beyond
- **Large outputs**: Write to `.claude/outputs/`, return path only

#### Mandatory Response Ending
```
STATUS: [complete|in_progress|blocked] | NEXT: [action] | KEY: [metrics]
```

## Prohibited Actions


1. **No Echo**: Never repeat input data back
2. **No Redundancy**: Don't repeat previous findings
3. **No Over-Explanation**: Keep explanations ≤3 sentences
4. **No Raw Content**: Use file paths instead of pasting
5. **No Unbounded Lists**: Always cap with "and N more..."

## Context Health Indicators


| %ctx | Status | Action |
|------|--------|--------|
| 0-40% | 🟢 Healthy | Normal operation |
| 40-60% | 🟡 Elevated | Consider summarizing |
| 60-80% | 🟠 High | Archive older exchanges |
| 80-100% | 🔴 Critical | Trim to essentials |

## Recovery Patterns


When context exceeds threshold:
1. Create checkpoint with current state
2. Write to `.claude/outputs/session-state.json`
3. Clear verbose history
4. Continue with checkpoint reference only

---
