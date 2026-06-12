---
name: crossprovider hermes dirty-state-classification-gates-clean-commits
description: Dirty state classification gates clean commits
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [commit-hygiene, dirty-state, change-scoping]
---

Before staging/committing, inventory ALL modified/untracked files. Classify each as task-owned (stage), durable evidence (stage), generated/session churn (exclude), or GTM artifacts (exclude). Never mix unrelated churn into implementation commits; if present, document as dirty-state exception separate from the commit.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
