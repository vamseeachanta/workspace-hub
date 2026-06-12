---
name: crossprovider gemini multi-repo-orchestration-parallel-submodule-sync
description: Multi-repo orchestration: parallel submodule sync followed by sequenced hub commit
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [git, workflow, multi-repo]
---

For synchronized commits across multiple repos, run submodule operations in parallel (collect exit codes), then serialize the hub commit/push after all submodules land. This avoids hub-first blocking on slow submodules and hub-last racing with concurrent pushes. Phase separation is the load-bearing constraint.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
