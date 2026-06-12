---
name: crossprovider hermes review-previous-batch-results-before-designing-n
description: Review previous batch results before designing next overnight run — avoid duplication
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [overnight-prompts, workflow]
---

Before crafting 5 new terminal prompts, check git log and issue status for prior batch completion. Terminal 4 (Doc Refresh) completed CAPABILITIES_SUMMARY before session started (already committed). Checking `git log --oneline` + `gh issue view` prevents duplicate assignments and builds momentum on existing progress.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
