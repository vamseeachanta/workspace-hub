---
name: claude-reflect-pattern-output-format
description: 'Sub-skill of claude-reflect: Pattern Output Format.'
version: 2.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Pattern Output Format

## Pattern Output Format


```yaml
patterns:
  - id: "pattern-001"
    type: "workflow"
    name: "TDD Test-First Pattern"
    description: "Tests created before implementation"
    evidence:
      - repo: "aceengineer-admin"
        commits: ["abc123", "def456"]
      - repo: "digitalmodel"
        commits: ["ghi789"]
    frequency: 0.85
    cross_repo_score: 0.9
    complexity_score: 0.7
    time_savings_score: 0.8
    final_score: 0.83
    recommended_action: "create_skill"
```
