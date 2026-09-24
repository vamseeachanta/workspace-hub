---
name: crossprovider gemini archive-recursion-glob-archive-md-not-just-archi
description: Archive recursion: glob archive/**/*.md, not just archive/*.md
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [glob-patterns, archive-discovery, common-pitfall]
---

Use pathlib.rglob or bash find -r; archive has date-partitioned subdirs (archive/YYYY-MM/*.md). Missing recursion silently skips files.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
