---
name: crossprovider codex pr-keywords-determine-github-auto-closure
description: PR keywords determine GitHub auto-closure
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github-workflow, issue-management, automation]
---

Use 'Closes #NNN' (not 'Refs #NNN') in PR descriptions to trigger automatic GitHub issue closure on merge. 'Refs' creates only a link; issues stay open and become zombie state. Common source of stale-open issues in large handoffs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
