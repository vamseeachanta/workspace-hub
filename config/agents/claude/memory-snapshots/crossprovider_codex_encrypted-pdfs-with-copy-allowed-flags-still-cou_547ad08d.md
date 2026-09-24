---
name: crossprovider codex encrypted-pdfs-with-copy-allowed-flags-still-cou
description: Encrypted PDFs with copy-allowed flags still count as DRM if policy forbids encrypted sources
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [drm-policy, encrypted-pdfs]
---

Some PDFs report "encrypted yes, copy allowed, change disallowed". Permission flags do not override encryption status; verify technical extractability separately from permissions metadata. If extraction policy forbids DRM, encrypted-but-copy-allowed still requires metadata-only treatment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
