---
name: crossprovider hermes plan-prerequisite-dependencies-must-have-explici
description: Plan prerequisite dependencies must have explicit resolution steps
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, prerequisites, multi-issue-coordination, implementation-readiness]
---

Plans that assume a sibling issue's work (e.g., #2515 assuming #2514 is available locally) need explicit prerequisite resolution steps, not just assertions like "#2514 is done." Check branch/commit availability, missing local files, and required merges. Prerequisite gaps are MAJOR if they block actual implementation, not just planning.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
