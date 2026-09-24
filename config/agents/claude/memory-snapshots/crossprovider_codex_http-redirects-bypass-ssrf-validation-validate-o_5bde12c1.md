---
name: crossprovider codex http-redirects-bypass-ssrf-validation-validate-o
description: HTTP redirects bypass SSRF validation; validate or disable them
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, ssrf, http-client, url-fetching]
---

Validating the original URL before calling requests.get() is insufficient if redirects are enabled. The final URL can bypass the SSRF guard and reach RFC1918 addresses. Either disable redirects by default or validate each redirect hop against the same policy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
