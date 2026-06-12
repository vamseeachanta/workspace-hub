---
name: crossprovider gemini team-lifecycle-automation-print-recipe-before-ex
description: Team lifecycle automation: print recipe before execute
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [automation, safety, verification]
---

spawn-team.sh prints instructions (mkdir + team-name) rather than auto-creating the directory. User reads, verifies, and manually runs the command. Safer than auto-execution and allows inspection before commitment. Follows print-before-execute pattern for high-consequence operations.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
