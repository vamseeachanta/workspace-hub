---
name: crossprovider hermes gh-repo-argument-requires-full-owner-repo-format
description: gh --repo argument requires full OWNER/REPO format
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-cli, batch-automation]
---

GitHub CLI's `--repo` flag does not accept bare repo names; it requires the fully qualified `OWNER/REPO` form. Batch issue creation scripts must construct this explicitly from context or user input. Discovered when `gh issue create --repo achantas-data` failed but `--repo vamseeachanta/achantas-data` succeeded.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
