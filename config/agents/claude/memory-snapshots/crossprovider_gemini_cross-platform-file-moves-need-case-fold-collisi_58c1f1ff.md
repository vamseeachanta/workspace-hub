---
name: crossprovider gemini cross-platform-file-moves-need-case-fold-collisi
description: Cross-platform file moves need case-fold collision detection
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [cross-platform, collision-detection, preflight]
---

When moving files across filesystems, check for case-insensitive collisions (e.g., `File.txt` already exists as `file.txt`) to prevent silent failures on case-insensitive filesystems (Windows, macOS). Preflight check required before apply. WRK-188 migration uses Python path iteration with `name.lower()` comparison.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
