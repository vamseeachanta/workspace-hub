---
name: crossprovider gemini reverse-drift-risk-from-fs-rmsync-cleanup-patter
description: Reverse-drift risk from fs.rmSync cleanup patterns
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [build-pipeline, state-mutation, risk-analysis, debugging]
---

Build scripts using fs.rmSync(distDir, ...) will erase any post-build edits to distDir files on next run. This is a latent risk if deploy scripts or manual interventions touch built artifacts. Document this hazard in plans involving cleanup-all patterns.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
