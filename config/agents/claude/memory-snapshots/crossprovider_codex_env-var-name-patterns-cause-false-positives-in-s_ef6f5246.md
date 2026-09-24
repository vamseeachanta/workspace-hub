---
name: crossprovider codex env-var-name-patterns-cause-false-positives-in-s
description: Env var name patterns cause false positives in secret detection regex
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [regex, secret-detection, false-positives]
---

Generic regexes matching token/secret/api_key patterns will flag legitimate env var names like TELEGRAM_HERMES_ALLOWED_USER_IDS. Use explicit allowlists (ENV_POINTER_FIELDS) to mark env var names as safe pointers; separate them from actual secret values that match stricter patterns.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
