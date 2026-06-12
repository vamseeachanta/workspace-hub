---
name: crossprovider codex resume-on-checkpoint-yaml-not-stage-evidence-yam
description: Resume on checkpoint.yaml, not stage-evidence.yaml claims
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [wrk-recovery, checkpoint, evidence-hierarchy]
---

WRK recovery state is authoritative from `checkpoint.yaml` (what actually happened), not `stage-evidence.yaml` (claimed completion). Missing checkpoint + claimed stages = incomplete recovery. Reconstruct from checkpoint or reset to last real stage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
