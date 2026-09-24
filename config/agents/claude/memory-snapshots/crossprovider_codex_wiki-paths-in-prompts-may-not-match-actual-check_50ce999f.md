---
name: crossprovider codex wiki-paths-in-prompts-may-not-match-actual-check
description: Wiki paths in prompts may not match actual checkouts; verify before planning
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [path-verification, planning-discipline]
---

Multiple ingest plans cite prompt paths like `/mnt/local-analysis/workspace-hub/llm-wiki/wikis/` that don't exist locally; actual checkout is `/mnt/local-analysis/llm-wiki`. Plans treating unverified paths as fact lead to discrepancies (file counts, scope, source location). Verification step must materialize actual path and enumerate actual file inventory before scope claims.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
