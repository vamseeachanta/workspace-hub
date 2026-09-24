---
name: crossprovider gemini pre-commit-encoding-hook-detects-utf-16-bom-befo
description: Pre-commit encoding hook detects UTF-16/BOM before Python parsers fail
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [encoding, git-hooks, cross-platform, data-integrity]
---

Hook reads first 4 bytes for BOM signatures (UTF-16 FE/FF, UTF-8 BOM EF/BB/BF), validates UTF-8 decode, and blocks commits on non-UTF-8 in YAML/Markdown configs. Post-merge/checkout warn-only behavior prevents checkout blockage while flagging legacy data. Fixes cross-platform (Windows+Linux) encoding drift that breaks downstream parsers.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
