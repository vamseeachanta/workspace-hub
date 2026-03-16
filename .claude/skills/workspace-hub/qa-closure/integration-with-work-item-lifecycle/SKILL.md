---
name: qa-closure-integration-with-work-item-lifecycle
description: 'Sub-skill of qa-closure: Integration with Work Item Lifecycle.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Integration with Work Item Lifecycle

## Integration with Work Item Lifecycle


This skill should be invoked by the orchestrator before closing any WRK item
that produces computational or analytical output:

```
Orchestrator flow:
  1. Agent completes task → signals "ready for QA"
  2. Orchestrator invokes /qa-closure WRK-NNN [artefact-paths...]
  3. /qa-closure runs Steps 1-5
  4. If PASS or WARN  → orchestrator proceeds to close WRK item
  5. If FAIL          → orchestrator blocks close, notifies user
```

---
