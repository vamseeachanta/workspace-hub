---
name: crossprovider hermes memory-drift-detection-and-bridging-is-fully-aut
description: Memory drift detection and bridging is fully automated with quality gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory-system, automation, quality-gate]
---

check-memory-drift.sh (exit 0/1) → pre-bridge-quality.sh (auto-compact if score 50–70, abort if <50) → bridge-hermes-claude.sh --commit. No human intervention required; bridges Hermes memory to Claude auto-memory when drift detected and quality passes threshold.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
