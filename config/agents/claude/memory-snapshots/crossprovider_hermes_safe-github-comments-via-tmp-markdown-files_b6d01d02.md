---
name: crossprovider hermes safe-github-comments-via-tmp-markdown-files
description: Safe GitHub comments via /tmp/ Markdown files
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-workflow, secret-safety, gh-cli]
---

When posting GitHub issue comments via `gh CLI`: write Markdown to `/tmp/<context>.md` first, then post via `gh issue comment`. Avoids shell interpolation and accidental secret leakage; safer than inline `gh ... --body`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
