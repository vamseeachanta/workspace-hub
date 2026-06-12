---
name: crossprovider hermes hook-security-findings-are-non-bypassable-unless
description: Hook security findings are non-bypassable unless user-approved
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, hooks, skills, credential-handling]
---

Credential-scraping patterns and security scanner findings in skills/docs are load-bearing constraints. Fix the skill content rather than bypassing with `--no-verify` or `--no-gpg-sign`. If user approves bypass, require explicit acknowledgment and understanding of the finding, and never preserve secrets in final artifacts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
