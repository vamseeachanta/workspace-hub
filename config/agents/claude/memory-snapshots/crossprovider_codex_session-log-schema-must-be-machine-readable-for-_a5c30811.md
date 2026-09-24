---
name: crossprovider codex session-log-schema-must-be-machine-readable-for-
description: Session log schema must be machine-readable for automated pattern detection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [session-analysis, drift-detection, log-schema]
---

Substring scanning of raw prose logs (e.g., detecting 'python3 ' or commit formats) is unreliable and produces false positives. Drift detectors and analysis tools require explicit event types and structured fields (e.g., command-execution events with argv, file-touch events with path, commit events with message). Define log schema before building detectors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
