---
name: crossprovider codex control-flags-must-persist-in-output-rows-even-w
description: Control flags must persist in output rows even when validated false
metadata:
  type: reference
  source: codex
  bridged: 2026-06-19
  tags: [privacy, output-contracts]
---

If a control flag (e.g., source_uploads_allowed, body_reads_allowed) is part of the output schema, it must appear in output rows even though validators confirm it is false. Dropping validated-false flags from outputs creates silent control-leakage risks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
