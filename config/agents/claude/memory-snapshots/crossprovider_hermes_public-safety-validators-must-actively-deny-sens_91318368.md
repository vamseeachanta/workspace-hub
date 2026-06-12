---
name: crossprovider hermes public-safety-validators-must-actively-deny-sens
description: Public-safety validators must actively deny sensitive metadata patterns, not rely on passive absence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, public-safety, fail-closed]
---

Vendor names, proprietary document titles, and client-specific metadata in artifacts are not caught by secret-scanning alone. Validators need explicit allow-lists that reject categories like vendor/proprietary/source-file titles in node/artifact content, not just regexes for secrets.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
