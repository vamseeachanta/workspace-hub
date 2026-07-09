---
name: crossprovider codex quality-contracts-must-aggregate-all-failure-mod
description: Quality contracts must aggregate all failure modes, not just happy-path counts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [data-quality, contracts, observability]
---

Data quality outputs should count parse failures, ambiguous joins, missing critical fields, and date-parsing failures—not just row counts and source-count summaries. Incomplete quality metrics hide systemic issues and prevent validation during production runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
