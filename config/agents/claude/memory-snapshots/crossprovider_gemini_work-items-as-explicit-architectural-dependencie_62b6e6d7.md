---
name: crossprovider gemini work-items-as-explicit-architectural-dependencie
description: Work items as explicit architectural dependencies
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [work-queue, dependencies, architecture]
---

WRK-080 (field blog post) couples to WRK-190 (NCS production data) and WRK-081 (calculator). Dependencies flow through work-queue frontmatter (`related`, `blocked_by`, `target_repos`). Agents and humans navigate work via dependency graphs in the queue.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
