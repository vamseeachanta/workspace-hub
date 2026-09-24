---
name: crossprovider codex comment-scanner-wiring-hazard-in-multi-stage-pip
description: Comment scanner wiring hazard in multi-stage pipelines
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [integration, governance, scanners, cli-dispatch]
---

Comment scanners often exist but are not integrated into the main CLI dispatch or closeout workflows. Always verify the scanner is called during artifact-publish and comment-post paths, not just in isolated tests. A passed test while the scanner is unreachable from production flows is a false-positive on governance enforcement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
