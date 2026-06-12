---
name: crossprovider hermes github-issue-creation-and-linking-from-overnight
description: GitHub issue creation and linking from overnight plans
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-workflow, overnight-planning]
---

Use `gh issue create --label cat:strategy,domain:gtm --body "$(cat <<EOF ...EOF)"` to create issues mid-session; immediately post follow-up comments linking issues via `gh issue comment` with issue numbers as markdown [#NNNN](url). Enables blocking/blocked_by tracking and cross-referencing across GTM campaigns.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
