---
name: crossprovider codex continuous-planning-pipeline-py-artifact-parsing
description: continuous-planning-pipeline.py artifact parsing accepts verdict tokens from anywhere in artifact body
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [parsing-bug, ci-cd, review-automation]
---

The parser accepts the first APPROVE/MINOR/MAJOR/UNAVAILABLE token anywhere in an artifact (including inside quoted prose like "No MAJOR blockers") and any line matching `Plan-SHA256: <64 hex>` even if inside fenced quotes. The parser should be hardened to accept these only from structured metadata headers, not from artifact body prose.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
