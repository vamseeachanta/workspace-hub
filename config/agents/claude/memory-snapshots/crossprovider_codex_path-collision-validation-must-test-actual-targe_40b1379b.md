---
name: crossprovider codex path-collision-validation-must-test-actual-targe
description: Path collision validation must test actual target paths, not placeholder rejections
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [testing-gaps, path-safety, collision-detection]
---

Testing that a validator rejects /tmp output is insufficient — the real collision risk is when output paths equal input paths that exist in the actual data directory (e.g., data/document-index/). Tests must probe input/output collision with concrete paths that would be used in production, not just verify placeholder paths are rejected.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
