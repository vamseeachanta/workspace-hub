---
name: crossprovider codex index-log-modifications-must-stage-referenced-fi
description: Index/log modifications must stage referenced files in same commit
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [git-workflow, index-management, artifact-consistency]
---

When updating index.md or log.md to reference new wiki pages, those pages must be staged (git add) in the same commit. Tracked metadata referencing untracked files creates broken references that persist after commit. Check git status before finalizing index/log changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
