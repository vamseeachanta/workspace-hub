---
name: compound-engineering-knowledge-extraction
description: 'Sub-skill of compound-engineering: Knowledge Extraction (+3).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Knowledge Extraction (+3)

## Knowledge Extraction


```
Delegate: Task(subagent_type=general-purpose)
- Analyze: what went well, what was surprising, what was hard
- Extract patterns (PAT-*): reusable approaches that worked
- Extract gotchas (GOT-*): traps encountered during implementation
- Extract tips (TIP-*): shortcuts or techniques discovered
- Extract decisions (ADR-*): architectural choices with rationale
- Extract corrections (COR-*): mistakes made and how they were fixed
```


## Knowledge Storage


```
Delegate: /knowledge capture
- Store each extracted entry with:
  - Confidence score based on review verdict
  - Tags linking to module, language, framework
  - Cross-references to the plan and review
```


## Skill Evolution


```
If any pattern scores > 0.7:
  Delegate: skill-learner
  - Evaluate if pattern warrants skill creation or enhancement
  - Score: (frequency * 0.3) + (cross_repo * 0.3) + (complexity * 0.2) + (time_savings * 0.2)
```


## Session Finalization


Update checkpoint:

```yaml
# .claude/compound-state/<session-id>.yaml
session_id: <session-id>
task: "<task description>"
phase: complete
plan_ref: specs/modules/<module>/plan.md
review_ref: .claude/compound-reviews/<session-id>.md
commits: [<sha1>, <sha2>, ...]
knowledge_entries: [PAT-xxx, GOT-xxx, TIP-xxx]
timestamp: <ISO-8601>
completed_at: <ISO-8601>
```
