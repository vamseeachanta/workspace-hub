---
name: crossprovider hermes aceengineer-strategy-nested-repo-affects-workflo
description: aceengineer-strategy nested repo affects workflow
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [environment, workflow, git-structure, repo-layout]
---

`workspace-hub/aceengineer-strategy/` is a separate git repo that requires `cd` before commits. Parent-directory commits (from workspace-hub/) won't touch strategy/ branch. This affects handoffs: strategy work needs `cd aceengineer-strategy && git commit` to land changes; parent workspace-hub commits won't include them.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
