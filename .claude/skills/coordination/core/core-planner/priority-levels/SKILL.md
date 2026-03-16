---
name: core-planner-priority-levels
description: 'Sub-skill of core-planner: Priority Levels (+1).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Priority Levels (+1)

## Priority Levels


| Priority | Description | Response Time |
|----------|-------------|---------------|
| Critical | Blocking issues | Immediate |
| High | Core functionality | Same day |
| Medium | Important features | Within sprint |
| Low | Nice-to-have | Backlog |

## Agent Allocation


```yaml
agent_capabilities:
  researcher: ["research", "analysis", "documentation"]
  coder: ["implementation", "api_design", "refactoring"]
  tester: ["unit_tests", "integration_tests", "e2e_tests"]
  reviewer: ["code_review", "security_audit", "performance"]
  planner: ["task_decomposition", "dependency_mapping", "risk_assessment"]
```
