---
name: crossprovider gemini fixture-redaction-via-pre-commit-regex-scan
description: Fixture redaction via pre-commit regex scan
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [security, fixtures, pre-commit]
---

Scan test fixtures for real email addresses, phone numbers, and known-domain references via pre-commit regex hook before commit to prevent credential leaks in git history.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
