---
name: crossprovider hermes artifact-refresh-before-re-running-adversarial-r
description: Artifact refresh before re-running adversarial review
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [code-review, prompt-hygiene]
---

Before re-invoking reviewers on same codebase, regenerate review prompts from latest `git diff` and save as new r7/r8/etc review files. Reviewers working from stale cached diffs miss fresh code changes and can rediscover already-fixed defects.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
