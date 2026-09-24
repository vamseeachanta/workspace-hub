---
name: crossprovider codex commit-prefix-classification-for-review-routing-
description: Commit-prefix classification for review routing is trivially gameable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [audit, process, evasion]
---

Splitting review requirements by prefix (feat/fix/refactor need review; docs/chore/test skip) can be circumvented by mislabeling substantive work. In multi-agent workflows, an agent can label a meaningful change as `chore:` or `docs:` and bypass review. Classification needs deeper analysis (file-path impact, diff size/complexity) or mandatory review on all categories.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
