---
name: crossprovider hermes markdown-linting-needs-repo-local-config-for-bus
description: Markdown linting needs repo-local config for business/strategy docs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [markdown, linting, config]
---

Default markdownlint rules enforce line-length and strict heading spacing; strategy/business docs intentionally use compact tables and template headings. Add `.markdownlint.jsonc` to disable conflicting rules (e.g., MD024, MD029) per repo rather than fighting 900+ default violations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
