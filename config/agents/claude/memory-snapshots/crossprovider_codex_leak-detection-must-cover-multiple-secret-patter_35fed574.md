---
name: crossprovider codex leak-detection-must-cover-multiple-secret-patter
description: Leak detection must cover multiple secret pattern classes
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [security, secrets-detection, payload-validation]
---

Path-only leak detection (e.g., `/mnt/ace`) misses credentials (password=, Bearer tokens, Set-Cookie headers) and private references (bare email addresses, internal hostnames). Detectors need multiple pattern classes: paths, auth headers, common secret formats.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
