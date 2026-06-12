---
name: crossprovider gemini large-model-files-1mb-in-git-cause-history-bloat
description: Large model files (>1MB) in git cause history bloat; use LFS or binary format
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [ml, git, performance]
---

4.8MB JSON model exports (e.g., sklearn GradientBoosting) expand every clone. Use Git LFS + .gitattributes, binary formats (.pkl, .bin) with hash verification, or .json.gz compression.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
