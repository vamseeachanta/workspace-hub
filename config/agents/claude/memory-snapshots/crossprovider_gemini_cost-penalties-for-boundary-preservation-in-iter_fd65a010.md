---
name: crossprovider gemini cost-penalties-for-boundary-preservation-in-iter
description: Cost penalties for boundary preservation in iterative edge collapse
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [mesh-decimation, boundary-handling, graph-algorithms]
---

When collapsing edges in mesh decimation, boundary edges (those with only one adjacent triangle) must carry a high cost penalty (e.g., 1e8) to ensure they are collapsed last or not at all, preserving the mesh boundary.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
