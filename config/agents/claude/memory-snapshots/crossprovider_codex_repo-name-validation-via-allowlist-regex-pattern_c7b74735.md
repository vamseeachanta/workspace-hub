---
name: crossprovider codex repo-name-validation-via-allowlist-regex-pattern
description: Repo-name validation via allowlist regex patterns
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bash, input-validation, injection]
---

Validate untrusted repo names with [[ ... ]] regex checks: reject empty, bare . or .., leading /, ../, /../, or |. Defense-in-depth for pipe-delimited result protocols prevents path traversal and injection when names come from internal config.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
