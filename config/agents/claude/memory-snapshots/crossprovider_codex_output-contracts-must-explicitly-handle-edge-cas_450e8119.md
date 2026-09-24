---
name: crossprovider codex output-contracts-must-explicitly-handle-edge-cas
description: Output contracts must explicitly handle edge cases
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, contracts, completeness]
---

Plans that specify primary outputs (e.g., 'true canonical gaps go into per-domain YAML') must also explicitly state the handling of edge cases (e.g., domain-mismatch records). Vague dispositions ('continue treating as not covered') fail acceptance criteria verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
