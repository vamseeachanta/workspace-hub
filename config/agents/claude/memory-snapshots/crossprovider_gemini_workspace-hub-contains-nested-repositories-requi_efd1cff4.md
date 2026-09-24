---
name: crossprovider gemini workspace-hub-contains-nested-repositories-requi
description: workspace-hub contains nested repositories requiring deep traversal
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workspace-hub, repository-structure, content-indexing]
---

workspace-hub has sub-repositories at multiple levels (3+ directory depth), not just top-level. Repository discovery and content-indexing scripts must traverse deeply and avoid stopping at the first .git directory.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
