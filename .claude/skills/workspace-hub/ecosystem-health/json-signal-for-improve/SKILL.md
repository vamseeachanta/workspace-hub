---
name: ecosystem-health-json-signal-for-improve
description: 'Sub-skill of ecosystem-health: JSON Signal (for /improve).'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# JSON Signal (for /improve)

## JSON Signal (for /improve)


When `--signal` flag is used, emit to `.claude/state/pending-reviews/ecosystem-review.jsonl`:

```json
{
  "timestamp": "2026-02-19T12:00:00Z",
  "source": "ecosystem-health",
  "severity": "fail|warn|info",
  "check": "check name",
  "detail": "human readable detail",
  "auto_fixed": false
}
```

One line per failed/warned check. `/improve` Phase 3 reads these signals.
