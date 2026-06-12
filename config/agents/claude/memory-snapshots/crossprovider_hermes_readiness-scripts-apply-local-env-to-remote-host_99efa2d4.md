---
name: crossprovider hermes readiness-scripts-apply-local-env-to-remote-host
description: Readiness scripts apply local env to remote hosts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [readiness, validation, multi-machine]
---

Readiness checks read env vars from local process, not remote. Per-host readiness requires actual remote verification; forwarded local state causes false positives/negatives.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
