---
name: crossprovider gemini session-signal-files-are-deliberately-tracked-fo
description: Session-signal files are deliberately tracked for learning pipelines
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [tracking, state, learning-pipeline]
---

Files in `.claude/state/session-signals/` are intentionally tracked in git (explicit `!` re-include in .gitignore) to feed learning-corpus pipelines (#1782, #1720). Size rotation and monitoring are needed to stay under platform limits, but .gitignore bypass is the wrong remedy.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
