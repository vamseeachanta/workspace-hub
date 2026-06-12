---
name: crossprovider hermes github-labels-are-portfolio-board-source-of-trut
description: GitHub labels are portfolio board source of truth
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [kanban-orchestration, portfolio-management, github-api]
---

For Kanban portfolio boards, GitHub labels (priority, category, domain, status) are authoritative; do not derive priority/sequencing from local plan files. Collect live issue state via `gh issue list` before generating board views.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
