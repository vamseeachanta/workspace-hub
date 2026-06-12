---
name: crossprovider hermes dirty-state-must-be-classified-before-staging-an
description: Dirty state must be classified before staging any repo-structure changes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, hygiene, commit-discipline]
---

Existing modified/untracked files must be audited and classified (intentional session work vs unrelated churn) before staging new commits. Never sweep unrelated dirt (generated artifacts, session logs, temporary data) into task commits.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
