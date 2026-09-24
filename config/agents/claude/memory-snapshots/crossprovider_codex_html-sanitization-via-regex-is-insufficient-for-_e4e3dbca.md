---
name: crossprovider codex html-sanitization-via-regex-is-insufficient-for-
description: HTML sanitization via regex is insufficient for XSS prevention
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, html-sanitization, xss]
---

Regex-based HTML hardening (protocol stripping, event handler removal) can be bypassed by entity-encoded payloads and obfuscated schemes. Use a proper HTML parser with explicit tag/attribute allowlists instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
