---
name: work-document-exit-step-6-output-summary
description: "Sub-skill of work-document-exit: Step 6 \u2014 Output Summary."
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Step 6 — Output Summary

## Step 6 — Output Summary


Print a clean exit summary to the user:

```
=== Work Document Exit — <SESSION_DATE> ===

Active WRK: <WRK_ID> — <title if available>
Handoff written to: <WRK_FILE or session-handoff.md>
Files changed: <count>
Branch: <BRANCH>

Next session: run /session-start to reload this handoff.

To commit now:
  git add <files>
  git commit -m "<commit message>"
==========================================
```
