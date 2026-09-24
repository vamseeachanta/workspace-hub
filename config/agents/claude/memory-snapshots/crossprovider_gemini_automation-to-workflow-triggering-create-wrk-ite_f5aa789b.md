---
name: crossprovider gemini automation-to-workflow-triggering-create-wrk-ite
description: Automation-to-workflow triggering: create WRK items on condition detection
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow, automation, human-in-loop]
---

When automated detection finds a condition (e.g., CLI version change), generate a work queue item (WRK) that prompts the human for next action, rather than only logging. Maintains human-in-the-loop review without requiring manual polling. Example: nightly-release-scan detects upgrade → creates WRK item prompting `/release-notes-adoption`.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
