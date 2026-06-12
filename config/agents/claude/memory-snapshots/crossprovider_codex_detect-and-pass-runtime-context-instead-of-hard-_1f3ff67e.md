---
name: crossprovider codex detect-and-pass-runtime-context-instead-of-hard-
description: Detect and pass runtime context instead of hard-coding auto-generated metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [metadata, automation, provenance]
---

Auto-generated WRK items that hard-code `computer: ace-linux-1` and `provider: claude` break when run on other machines or by different automation providers. Derive execution metadata from runtime (hostname, actual agent) and pass into generators instead of defaulting.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
