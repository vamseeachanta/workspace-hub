---
name: crossprovider hermes multi-artifact-export-pattern-for-dashboards
description: Multi-artifact export pattern for dashboards
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-generation, reporting, quality-gates]
---

Portfolio board refresh emits three synchronized artifacts: JSON data layer (for programmatic use), Markdown board view (for navigation), HTML dashboard (for visualization). All three verify counts/links before push; credential scan mandatory before git push.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
