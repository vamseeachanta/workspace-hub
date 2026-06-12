---
name: crossprovider codex multi-repo-status-reduction-needs-explicit-prece
description: Multi-repo status reduction needs explicit precedence — fail > warn > skip > pass
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [harness-design, schema-design]
---

When aggregating repo results into a summary, define explicit reduction logic (e.g., if any repo fails, overall status is fail; else warn; else pass). Without this, implementations diverge and CI gates become unreliable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
