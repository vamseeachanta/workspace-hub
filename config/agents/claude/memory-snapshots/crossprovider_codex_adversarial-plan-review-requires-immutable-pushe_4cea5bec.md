---
name: crossprovider codex adversarial-plan-review-requires-immutable-pushe
description: Adversarial plan review requires immutable pushed commits before review cycle
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [workflow, planning, multi-provider-review]
---

Write the plan, push it to a fixed commit, then dispatch reviewers (Claude/Codex/Gemini) against that exact commit hash. This prevents 'review drift' where local changes alter the artifact while external reviewers are still working. Reviewers cite line numbers and diffs anchored to the pushed commit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
