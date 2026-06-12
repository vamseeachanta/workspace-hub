---
name: crossprovider hermes external-urls-leak-credentials-via-userinfo-in-g
description: External URLs leak credentials via userinfo in generator/validator
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, validation, secret-safety]
---

URLs like `https://token@example.com` or `https://user:pass@example.com` are accepted by tools that only check scheme/path. Reject URL userinfo by checking `urlparse(...).username`, `.password`, and userinfo in netloc. Add credential-bearing URL tests to catch regressions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
