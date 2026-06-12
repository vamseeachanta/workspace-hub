---
name: crossprovider codex re-validate-http-redirect-targets-against-ssrf-p
description: Re-validate HTTP redirect targets against SSRF policy
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [security, url-fetching, ssrf]
---

URL fetchers that validate initial URLs before calling requests.get() are still vulnerable if redirects (30x) point to localhost/RFC1918 ranges. Must validate `response.url` against the same SSRF policy, ideally each redirect hop, to close the bypass.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
