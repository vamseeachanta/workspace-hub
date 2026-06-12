---
name: crossprovider codex path-control-character-validation-prevents-hidde
description: Path control-character validation prevents hidden data loss
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [migrations, data-safety, path-validation]
---

File migrations should validate paths for control characters (ord < 32) before copy/centralization; undetected control chars silently corrupt filenames in manifests and checksums. Add this as early validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
