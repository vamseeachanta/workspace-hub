---
name: crossprovider codex substring-matching-detection-falsely-exempts-vio
description: Substring-matching detection falsely exempts violations when negation phrase appears in unrelated context
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pattern-detection, shell-safety, false-negatives, drift-detection]
---

Pattern detection using substring matching (e.g., `[[ $cmd == *uv run* ]] && [[ $cmd == *python3* ]]`) fails to catch violations when the exclusion phrase appears separately. Example: `echo uv run && python3 scripts/foo.py` reports zero violations when python3 is bare. Use regex anchors or structured parsing instead of substring scans for compliance detection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
