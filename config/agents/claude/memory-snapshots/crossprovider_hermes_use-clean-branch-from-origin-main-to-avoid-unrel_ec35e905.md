---
name: crossprovider hermes use-clean-branch-from-origin-main-to-avoid-unrel
description: Use clean branch from origin/main to avoid unrelated work contamination
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, branch-hygiene, scope-isolation]
---

When local main has unpushed commits unrelated to current task, create plan/review branch from `origin/main` instead of local main. Prevents accidental push of unrelated work and keeps the approval chain isolated to the approved scope.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
