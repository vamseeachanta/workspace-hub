---
name: crossprovider codex tools-accepting-partial-inputs-become-silently-n
description: Tools accepting partial inputs become silently non-reproducible
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [tool-design, partial-inputs, reproducibility]
---

When a tool accepts summarized or capped inputs (e.g., a 120-row corpus summary of a 534-row source), the generated report is non-reproducible and silently incomplete. Users think they're running analysis over the full corpus but get partial results. Either reject partial inputs outright, or force explicit scope flags (e.g., `--source-count=120-of-534`) and include them in output metadata and documentation. In #268, the coverage report was generated from a capped manifest without noting the scope limit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
