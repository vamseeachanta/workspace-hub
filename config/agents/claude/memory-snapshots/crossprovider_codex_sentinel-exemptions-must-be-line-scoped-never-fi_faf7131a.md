---
name: crossprovider codex sentinel-exemptions-must-be-line-scoped-never-fi
description: Sentinel exemptions must be line-scoped, never file-blanket
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, rule-scanning, redaction, backdoor-risk]
---

When using example lines to exempt/allow patterns in deny-lists or rule scanners, scope exemption to that exact line only. File-level blanket exempts are backdoors—a file containing both an example line and a real leak will pass the scanner. Use per-value sentinels or line-level markers, never per-file allowlists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
