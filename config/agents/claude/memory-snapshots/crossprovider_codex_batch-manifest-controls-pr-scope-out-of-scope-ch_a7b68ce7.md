---
name: crossprovider codex batch-manifest-controls-pr-scope-out-of-scope-ch
description: Batch manifest controls PR scope; out-of-scope changes must be split
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [batch-review, scope-control, pr-split]
---

A batch's manifest CSV (e.g., `manifest.csv` in a vision-review batch) explicitly lists which rows should be changed. Any queue or index changes outside those rows indicate out-of-scope regeneration or accidental drift. Require a separate cleanup PR for scope creep to preserve audit clarity—approval of batch PRs assumes scope boundaries are tight.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
