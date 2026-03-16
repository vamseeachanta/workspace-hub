---
name: work-document-exit
description: "Documents the active WRK item's session state \u2014 work done, files\
  \ changed, next steps \u2014 writes a Session Handoff section to the WRK file, stages\
  \ files, and exits cleanly.\n"
version: 1.0.0
updated: 2026-02-24
category: workspace-hub
triggers:
- work document exit
- document and exit
- handoff
- exit session
- prepare handoff
- wrap this WRK
- document work
related_skills:
- session-end
- save
- session-start
- workflow-gatepass
capabilities:
- wrk-state-capture
- session-handoff
- staged-commit-prep
- active-wrk-resolution
requires:
- .claude/work-queue/
- git
see_also:
- work-document-exit-what-it-does
- work-document-exit-step-1-identify-the-active-wrk-item
- work-document-exit-step-2-collect-session-context
- work-document-exit-step-3-write-session-handoff-section
- work-document-exit-work-done-this-session
- work-document-exit-step-4-stage-files
- work-document-exit-step-5-clear-active-wrk-state
- work-document-exit-step-6-output-summary
- work-document-exit-no-active-wrk-fallback
- work-document-exit-integration-with-session-end
invoke: work-document-exit
---

# Work Document Exit

## When to Use

- Before `/clear` when a WRK item is still in progress
- When handing off to another session or machine
- Before an unexpected exit with work partially done
- When `/session-end` is run while a WRK item is active

## Sub-Skills

- [What It Does](what-it-does/SKILL.md)
- [Step 1 — Identify the Active WRK Item](step-1-identify-the-active-wrk-item/SKILL.md)
- [Step 2 — Collect Session Context](step-2-collect-session-context/SKILL.md)
- [Step 3 — Write Session Handoff Section](step-3-write-session-handoff-section/SKILL.md)
- [Work Done This Session (+5)](work-done-this-session/SKILL.md)
- [Step 4 — Stage Files](step-4-stage-files/SKILL.md)
- [Step 5 — Clear Active WRK State](step-5-clear-active-wrk-state/SKILL.md)
- [Step 6 — Output Summary](step-6-output-summary/SKILL.md)
- [No-Active-WRK Fallback](no-active-wrk-fallback/SKILL.md)
- [Integration with /session-end](integration-with-session-end/SKILL.md)
