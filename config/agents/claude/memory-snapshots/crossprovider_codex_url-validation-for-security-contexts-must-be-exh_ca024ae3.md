---
name: crossprovider codex url-validation-for-security-contexts-must-be-exh
description: URL validation for security contexts must be exhaustive on scheme/query/fragment
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [security, url-validation, github-api]
---

Checking only netloc/path/fragment of GitHub URLs missed http:// (non-HTTPS) and query parameters. Security-critical URL validation must exhaustively check scheme, query parameters, and fragment structure, not just path/host.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
