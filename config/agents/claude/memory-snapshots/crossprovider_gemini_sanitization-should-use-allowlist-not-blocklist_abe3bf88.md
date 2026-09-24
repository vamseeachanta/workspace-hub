---
name: crossprovider gemini sanitization-should-use-allowlist-not-blocklist
description: Sanitization should use allowlist, not blocklist
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [security, input-validation, sanitization]
---

For WRK_ID and other user inputs, whitelist safe characters (alphanumeric + hyphens) rather than blacklist unsafe ones. Allowlist prevents path traversal and injection more reliably. WRK-658 security finding.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
