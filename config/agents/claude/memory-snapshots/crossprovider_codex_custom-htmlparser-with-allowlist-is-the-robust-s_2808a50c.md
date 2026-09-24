---
name: crossprovider codex custom-htmlparser-with-allowlist-is-the-robust-s
description: Custom HTMLParser with allowlist is the robust sanitization pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, html-sanitization, python-stdlib]
---

Implement a `HTMLParser` subclass that explicitly allows only safe tags and attributes, validates URL schemes with `urlparse()`, and escapes all user data. This prevents both attribute injection and protocol attacks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
