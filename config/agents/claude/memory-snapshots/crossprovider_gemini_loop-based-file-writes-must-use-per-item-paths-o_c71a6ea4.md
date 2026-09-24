---
name: crossprovider gemini loop-based-file-writes-must-use-per-item-paths-o
description: Loop-based file writes must use per-item paths or explicit append logic
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [plan-review, correctness, pseudocode]
---

Writing to the same file inside a loop overwrites previous iterations, preserving only the final entry. When pseudocode loops over collections, either place outputs in per-item subdirectories or use append-mode handles; single-write-per-loop-iteration is a data-loss hazard.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
