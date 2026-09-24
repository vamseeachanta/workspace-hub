---
name: crossprovider codex project-conventions-affect-review-verdicts-infer
description: Project conventions affect review verdicts; infer from existing codebase data
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [conventions, domain-knowledge, review-accuracy]
---

Domain-specific conventions (e.g., how metrics like `pct_resolved` are calculated, whether deferred rows count as resolved) determine whether findings are valid. Infer conventions from existing data to avoid false MAJOR findings; document explicitly so reviewers don't re-discover them.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
