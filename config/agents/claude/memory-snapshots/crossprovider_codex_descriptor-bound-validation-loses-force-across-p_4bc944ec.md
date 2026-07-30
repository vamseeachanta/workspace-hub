---
name: crossprovider codex descriptor-bound-validation-loses-force-across-p
description: Descriptor-bound validation loses force across pathname operations
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [pathname-toctou, file-descriptor-safety, binding-scope]
---

File descriptor binding (O_NOFOLLOW + fstat to verify identity) is voided once control returns to pathname-based operations. Origin changes in `.git/config` or target path replacements after the final fd-bound check bypass all prior identity validation. Binding must extend through all subsequent operations via descriptor-relative calls, or be re-verified immediately before each critical operation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
