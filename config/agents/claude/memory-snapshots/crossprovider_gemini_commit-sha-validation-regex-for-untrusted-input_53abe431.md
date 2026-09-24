---
name: crossprovider gemini commit-sha-validation-regex-for-untrusted-input
description: Commit SHA validation regex for untrusted input
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [security, git, validation]
---

When accepting commit references from external or untrusted sources, validate with regex `^[0-9a-fA-F]{7,40}$` to ensure 7–40 hex characters before passing to git commands. Prevents command injection via malformed commit hashes.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
