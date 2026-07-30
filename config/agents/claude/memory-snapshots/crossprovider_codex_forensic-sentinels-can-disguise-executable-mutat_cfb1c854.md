---
name: crossprovider codex forensic-sentinels-can-disguise-executable-mutat
description: Forensic sentinels can disguise executable mutations as data
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [security, data-integrity]
---

If mutations are stored or logged as strings, weak sentinel parsing allows execution to hide as data. Must explicitly parse, validate, and fail-closed on sentinel violations to prevent hidden executable mutations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
