---
name: crossprovider codex file-existence-verification-guards-against-stale
description: File existence verification guards against stale claims
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [verification, file-safety, command-safety]
---

Use `ls -la -- "$f"` with flag-injection guard (double quotes, pathspec) to verify file existence before citing files as evidence in plans or review summaries. Attested evidence blocks verify this at dispatch time; otherwise, missing files in plan-text become undetected defects.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
