---
name: crossprovider codex direct-interpolation-of-untrusted-fields-into-ht
description: Direct interpolation of untrusted fields into HTML enables stored XSS
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [security-xss, html-reports, output-encoding]
---

Inserting API numbers, well names, or activity codes directly into HTML report strings without escaping allows malicious values to execute JavaScript. Use html.escape() or templating engines with auto-escaping before any untrusted data enters HTML.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
