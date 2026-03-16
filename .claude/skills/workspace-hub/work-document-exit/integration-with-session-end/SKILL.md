---
name: work-document-exit-integration-with-session-end
description: 'Sub-skill of work-document-exit: Integration with /session-end.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Integration with /session-end

## Integration with /session-end


This skill is designed to run as a sub-step of `/session-end` when a
WRK item is active. Call it before Step 5 (snapshot + clear) in the
`session-end` workflow.

Manual invocation: `/work-document-exit`
Auto-trigger: When `/session-end` detects a working/ item with `percent_complete < 100`

---

*Counterpart to `/session-start` context loading. Use together for clean multi-session WRK handoffs.*
