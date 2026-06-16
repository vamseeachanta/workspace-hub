---
name: crossprovider codex code-review-sessions-accumulate-1gb-stale-artifa
description: Code-review sessions accumulate 1GB+ stale artifacts in /tmp
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [cleanup, tmp, review, operational]
---

Adversarial review, workflow, and image-capture sessions leave review logs, workflow scratch, and repo clones under /tmp that persist after the session ends. Sessions should clean up review artifacts before exit, or a scheduled nightly cleanup job should target review-session patterns (wf*, codex-review-*, vision-review*) after a safety delay.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
