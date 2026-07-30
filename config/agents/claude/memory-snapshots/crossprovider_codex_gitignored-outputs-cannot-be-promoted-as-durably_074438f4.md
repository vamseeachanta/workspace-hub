---
name: crossprovider codex gitignored-outputs-cannot-be-promoted-as-durably
description: Gitignored outputs cannot be promoted as durably publishable
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [publishing, git-workflow, reproducibility]
---

Generated artifacts that are gitignored (like the 1,390-row BSEE atlas dated June 21) become invisible to CI and cannot be reproduced; date, repair status, and source lineage are lost. If an output must be published, it must be either committed or regenerated deterministically from tracked sources in the pipeline.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
