---
name: crossprovider codex dry-run-writes-outputs-but-not-to-repo
description: Dry-run writes outputs but not to repo
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [testing, deployment, transactional-systems]
---

Dry-run mode still writes local outputs (topics, runtime slices) but skips repo commits/pushes. Failure to push does not mean output generation failed; these are distinct phases with independent success criteria.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
