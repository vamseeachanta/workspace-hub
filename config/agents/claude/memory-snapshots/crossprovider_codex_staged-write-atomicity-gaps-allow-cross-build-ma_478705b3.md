---
name: crossprovider codex staged-write-atomicity-gaps-allow-cross-build-ma
description: Staged write atomicity gaps allow cross-build manifest inconsistency
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [atomicity, consistency, write-protocol, data-pipeline]
---

When raw manifest, normalized outputs, curated outputs, and their manifests are written in separate steps (not staged/promoted atomically), a failed run can leave manifests from one build and curated outputs from another. Data consumers see inconsistent versions. Fix: stage all outputs before promotion, version build directories, or ensure manifest writes are atomic with output writes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
