---
name: crossprovider gemini quadric-error-metrics-boundary-vertices-need-pen
description: Quadric Error Metrics: boundary vertices need penalty costs to preserve topology
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [mesh-simplification, topology-preservation, qem-algorithm]
---

In QEM mesh decimation (Garland-Heckbert 1997), boundary edges (appearing in only one triangle) should carry a high penalty cost (e.g., 1e8) so they collapse last. Without penalties, boundary topology degrades first even though interior mesh quality is acceptable. Identify boundaries by undirected edge-count == 1.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
