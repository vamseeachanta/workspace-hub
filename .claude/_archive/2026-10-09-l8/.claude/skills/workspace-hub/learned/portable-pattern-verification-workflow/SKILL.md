---
name: portable-pattern-verification-workflow
description: Multi-package implementation with verification strategy for cross-platform configuration hardening
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["architecture", "verification", "portability", "configuration"]
---

# Portable Pattern Verification Workflow

When implementing multi-phase changes to shared config files: (1) read all target files and instruction context in parallel, (2) identify existing portable patterns in the codebase as baseline precedent, (3) implement packages sequentially with specific ordering when targeting the same file, (4) verify execution using grep to confirm only comments/diagnostics remain in actual call paths, never execution strings. Use `command -v` probes for safe capability detection rather than direct command invocation.