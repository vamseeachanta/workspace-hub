---
name: skills-curation-phase-2-knowledge-graph-review
description: "Sub-skill of skills-curation: Phase 2 \u2014 Knowledge Graph Review."
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Phase 2 — Knowledge Graph Review

## Phase 2 — Knowledge Graph Review


**Purpose**: identify which skill domains are load-bearing for current work and which are data-thin.

**Steps:**

1. Load `SKILLS_GRAPH.yaml`
2. Load all active WRK items from `.claude/work-queue/pending/` and `.claude/work-queue/working/`
3. For each skill node in the graph, compute a demand score:

```
demand_score = (wrk_references × 3) + (edge_count × 1) + (commit_activity × 2)
depth_score  = content_length_bucket + connected_skill_count
gap_score    = demand_score - depth_score   # positive = high demand, low data
```

4. Sort skills by gap_score descending; top 5 become research targets for Phase 3
5. Flag skills with `demand_score == 0` as archival candidates (no connection to current work)
6. Flag domains with `demand_score > threshold` but **no existing skill** as new skill candidates

**Output:**

```yaml
# Written to .claude/state/skills-graph-review-log.jsonl (one line per run)
{
  "ts": "...",
  "run_id": "...",
  "high_gap_skills": [...],
  "archival_candidates": [...],
  "new_skill_candidates": [...],
  "research_targets": [...]
}
```

---
