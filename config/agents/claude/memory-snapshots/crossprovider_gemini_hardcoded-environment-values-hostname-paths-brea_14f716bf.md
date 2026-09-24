---
name: crossprovider gemini hardcoded-environment-values-hostname-paths-brea
description: Hardcoded environment values (hostname, paths) break multi-machine portability
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [portability, hardcoded-values, multi-environment]
---

Code like `computer: ace-linux-1` in metadata fails when run on different machines. Replace with runtime detection: `platform.node()` for hostname, environment variables for paths, or machine-agnostic identifiers. Assume multi-machine execution by default; environment-specific values rot into stale gotchas.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
