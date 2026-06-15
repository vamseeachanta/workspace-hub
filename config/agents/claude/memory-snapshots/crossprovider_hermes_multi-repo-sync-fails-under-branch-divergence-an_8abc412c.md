---
name: crossprovider hermes multi-repo-sync-fails-under-branch-divergence-an
description: Multi-repo sync fails under branch divergence and refspec limits
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, multi-repo, concurrency]
---

Repository sync operations fail when branches diverge (client-b case), fetch refspec limited to master/main only, or concurrent git operations create lock contention. Parallel agent fleets running >20 git processes cause chained operations to hang in D-state (~19min observed on large repos).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
