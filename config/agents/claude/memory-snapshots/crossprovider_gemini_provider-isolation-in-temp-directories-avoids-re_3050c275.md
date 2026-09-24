---
name: crossprovider gemini provider-isolation-in-temp-directories-avoids-re
description: Provider isolation in temp directories avoids repo-context hangs
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [provider-integration, reliability, performance]
---

Running provider CLI tools in isolated temporary directories (separate from repo root) avoids initialization hangs and tool drift. Particularly effective for non-interactive review transport where repo context causes timeouts.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
