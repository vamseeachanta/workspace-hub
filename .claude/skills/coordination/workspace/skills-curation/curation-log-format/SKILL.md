---
name: skills-curation-curation-log-format
description: 'Sub-skill of skills-curation: Curation Log Format.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Curation Log Format

## Curation Log Format


State is persisted at `.claude/state/curation-log.yaml`:

```yaml
version: "1.0"
last_run: "2026-02-20T10:00:00Z"
cadence: weekly   # current active cadence
consecutive_low_runs: 0
runs:
  - run_id: "2026-02-20-001"
    ts: "2026-02-20T10:00:00Z"
    phases_run: [candidates, graph_review, online_research, gap_triage, health_check]
    yield:
      skills_created: 2
      skills_updated: 1
      wrk_items_created: 0
      research_findings: 6
      gaps_closed: 2
    health_warnings: []
    cadence_after: weekly
```

Research details go to `.claude/state/skills-research-log.jsonl` (one JSONL line per run).

Graph review details go to `.claude/state/skills-graph-review-log.jsonl` (one JSONL line per run).

---
