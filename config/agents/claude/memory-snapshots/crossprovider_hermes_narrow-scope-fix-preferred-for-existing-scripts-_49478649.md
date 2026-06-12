---
name: crossprovider hermes narrow-scope-fix-preferred-for-existing-scripts-
description: Narrow scope fix preferred for existing scripts with limited current behavior
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, risk-management, scope]
---

When a script (e.g., `hermes-session-export.sh`) has limited error-handling today (e.g., fail-open with `|| true`), keep the fix narrow to that surface rather than proposing a broader redesign (e.g., comprehensive failure-handling overhaul). Narrow fixes reduce risk, testing surface, and scope creep; document what the script does NOT do today to avoid misleading reviewers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
