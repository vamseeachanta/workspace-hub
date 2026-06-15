---
name: crossprovider codex spaced-secret-patterns-bypass-literal-string-red
description: Spaced secret patterns bypass literal-string redaction
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [privacy, redaction, secret-handling, issue-259]
---

Redaction checking for literal strings like AWS_SECRET_ACCESS_KEY= misses variants with spaces like AWS Secret Access Key: value. Issue #259: gh stderr and generated prompts leaked secrets with spacing. Use regex-based patterns for secret matching.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
