---
name: crossprovider hermes pre-launch-collision-detection-for-parallel-asyn
description: Pre-launch collision detection for parallel async issues
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, async-coordination, github-workflow]
---

When Hermes spawns parallel sessions for related issues, implement a pre-launch check: gh issue view <upstream_issue> --comments to detect if upstream work (e.g., #2696 routing changes affecting #2657 paths) has already landed or is in flight. If overlap detected, DEFER and post deferral comment explaining the dependency.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
