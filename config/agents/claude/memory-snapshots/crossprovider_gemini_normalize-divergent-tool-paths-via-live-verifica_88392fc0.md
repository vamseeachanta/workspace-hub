---
name: crossprovider gemini normalize-divergent-tool-paths-via-live-verifica
description: Normalize divergent tool paths via live verification
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow-standardization, portability, verification]
---

When standardizing workflows across machines, documentation sources often disagree on bootstrap paths (/usr/lib/openfoam vs /opt/openfoam). Verify the canonical path by running against live systems first, then document and enforce one path. Don't preserve multiple paths as simultaneous truths.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
