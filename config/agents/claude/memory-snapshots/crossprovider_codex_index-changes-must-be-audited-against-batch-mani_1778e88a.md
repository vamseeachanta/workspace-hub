---
name: crossprovider codex index-changes-must-be-audited-against-batch-mani
description: Index changes must be audited against batch manifest scope
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [verification-pattern, index-safety]
---

Document-index rebuilds silently include out-of-scope rows from live queues (e.g., pipeline-engineering rows after batch #683) because the generator treats all live queues as source. Audit pattern: extract manifest → compare index changes → flag additions outside batch scope; `--check` validation alone is insufficient.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
