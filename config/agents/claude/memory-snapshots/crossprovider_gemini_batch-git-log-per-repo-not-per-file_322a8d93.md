---
name: crossprovider gemini batch-git-log-per-repo-not-per-file
description: Batch git log per-repo, not per-file
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [git-performance, shell-scripting, doc-drift]
---

Spawning `git log` for each file in a large repo is N+1 and prohibitively slow. Single repository-wide `git log` call with result cached in memory provides O(1) lookup for file staleness checks. Reduces runtime from minutes to seconds on 20K+ file repos.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
