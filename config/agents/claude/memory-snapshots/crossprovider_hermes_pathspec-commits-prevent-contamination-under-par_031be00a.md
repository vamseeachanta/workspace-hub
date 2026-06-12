---
name: crossprovider hermes pathspec-commits-prevent-contamination-under-par
description: Pathspec commits prevent contamination under parallel-agent load
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, multi-agent, commit-safety, contamination]
---

With many dirty/untracked files from parallel agents, use git commit -- <paths> to limit scope. Full-tree commits sweep unrelated changes into the wrong commit context.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
