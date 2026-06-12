---
name: crossprovider hermes post-to-github-only-when-major-0-across-all-prov
description: Post to GitHub only when MAJOR=0 across all providers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-verdict, posting-gate, verdict-threshold]
---

A plan moves from local draft to status:plan-review (posted to GH with label) only if all three providers have MAJOR=0. If any provider is MAJOR, keep the plan local and revise; posting prematurely creates GitHub-vs-local state drift.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
