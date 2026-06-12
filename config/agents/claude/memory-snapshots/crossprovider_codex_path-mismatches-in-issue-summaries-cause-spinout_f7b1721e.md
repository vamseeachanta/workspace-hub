---
name: crossprovider codex path-mismatches-in-issue-summaries-cause-spinout
description: Path mismatches in issue summaries cause spinout confusion (knowledge/wikis vs wikis)
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [path-naming, repo-spinouts, scout-reports]
---

llm-wiki issue #28/#29 summaries reference `knowledge/wikis/...` paths, but actual repo uses `wikis/...`. When scope-planning complex spinouts or cross-repo references, verify repo-local paths early. Scout reports should establish confirmed paths before implementation to avoid rework.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
