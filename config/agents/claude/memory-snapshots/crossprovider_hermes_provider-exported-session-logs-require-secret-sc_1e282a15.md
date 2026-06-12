---
name: crossprovider hermes provider-exported-session-logs-require-secret-sc
description: Provider-exported session logs require secret scanning before commit
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [secrets, provider-logs, commit-safety]
---

Generated provider session exports (from hermes-session-export.sh, codex-session-export.sh, gemini-session-export.sh) contain raw conversation data and may include API keys, tokens, credentials, or other secrets. Scan 82+ candidate changed files for secrets before committing; a focused scan can identify and exclude sensitive values.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
