---
name: crossprovider hermes ai-utilization-tracking-is-stale-by-design-no-re
description: AI utilization tracking is stale by design (no refresh cron)
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [utilization, quota-tracking, monitoring-gap]
---

agent-quota.json (10+ days stale), claude_usage.json (Jan 2025 placeholder), codex/gemini usage (never populated) show no automated refresh. cost-tracking.jsonl (67.7 MB, 246K records, Apr 4) is the only fresh source. No cron job refreshes quotas, and check_claude_usage.sh never executed. Gemini and Codex spend are invisible by default; utilization data degrades linearly with session age.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
