---
name: crossprovider codex legacy-csv-row-position-recovery-without-manglin
description: Legacy CSV row-position recovery without mangling
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [csv-parsing, backwards-compat, normalization]
---

Old verification queues have parse_status shifted into wrong columns. Detect positional-format rows via _looks_like_positional_table_row(), extract into correct fields; add page-column fallback mapping to preserve legacy data during normalization.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
