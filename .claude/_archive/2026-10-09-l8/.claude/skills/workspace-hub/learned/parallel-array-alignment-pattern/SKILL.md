---
name: parallel-array-alignment-pattern
description: Maintain index synchronization between parallel arrays when adding new entries to preserve label-path mappings
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["bash", "data-structures", "array-handling", "configuration-management"]
---

# Parallel Array Alignment Pattern

When modifying bash scripts that use parallel arrays (e.g., `SOURCE_LABELS` and `SOURCE_PATHS`), ensure new entries are appended to both arrays at matching indices. The loop that consumes these arrays typically iterates by index: `for i in "${!SOURCE_LABELS[@]}"; do ... "${SOURCE_LABELS[$i]}" ... "${SOURCE_PATHS[$i]}"`.

Before adding an entry, verify the current array length is identical across all parallel arrays. Add your new element to each array at the same position to prevent off-by-one misalignment that breaks the label-path relationship.